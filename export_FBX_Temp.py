# -*- coding: utf-8 -*-
"""
export_FBX_Temp.py

CAM 오브젝트의 애니메이션 키를 기준으로 컷(Cut)을 분할하여
각 컷별로 root와 CAM 오브젝트를 FBX로 각각 일괄 익스포트합니다.
컷 번호(예: C0110 -> C0111)와 리비전 접미사(예: _R00) 패턴에 맞춰 별도 파일로 내보냅니다.
"""

import os
import re
import maya.cmds as cmds
import maya.mel as mel

def run_export():
    # 1. 씬 경로 및 기본 저장 경로 검사
    scene_path = cmds.file(q=True, sn=True)
    if scene_path:
        scene_dir = os.path.dirname(scene_path).replace('\\', '/')
        scene_base = os.path.splitext(os.path.basename(scene_path))[0]
    else:
        scene_dir = "E:/ssb_workspace/ELV8/Fansell/CHB/Shot"
        scene_base = "Fansel_RouletteTitle_CHB_S03-C0110_R00"
        print("Scene is not saved. Using default directory and filename.")
        
    if not os.path.exists(scene_dir):
        try:
            os.makedirs(scene_dir)
        except Exception as e:
            cmds.warning("Cannot create output directory: %s" % e)
            
    # 2. 파일 이름에서 컷 번호 패턴 및 리비전 접미사 파싱
    # 예: Fansel_RouletteTitle_CHB_S03-C0110_R00
    # m.group(1): Fansel_RouletteTitle_CHB_S03
    # m.group(2): -
    # m.group(3): 0110
    # m.group(4): _R00
    m = re.search(r'^(.*?)([-_])C(\d+)(.*)$', scene_base)
    if m:
        base_prefix = m.group(1)
        separator = m.group(2)
        start_cut_num = int(m.group(3))
        padding_len = len(m.group(3))
        base_suffix = m.group(4)
    else:
        base_prefix = scene_base
        separator = "_"
        start_cut_num = 1
        padding_len = 2
        base_suffix = ""

    # 3. CAM 오브젝트의 고유 애니메이션 키 수집 및 정렬
    cam_node = "CAM"
    if not cmds.objExists(cam_node):
        cmds.error("CAM object does not exist in the scene. Cannot split cuts.")
        return
        
    keys = cmds.keyframe(cam_node, query=True, timeChange=True)
    if not keys:
        cmds.error("No animation keys found on CAM object.")
        return
        
    # 소수점 프레임 반올림 후 중복 제거 및 정렬
    sorted_keys = sorted(list(set(int(round(k)) for k in keys)))
    print("Detected CAM keyframes at frames: %s" % sorted_keys)
    
    # 4. 각 키별 익스포트 범위(컷) 계산 및 파일 이름 정의 (각 키부터 2프레임씩 익스포트)
    cuts = []
    for idx, key in enumerate(sorted_keys):
        start_val = int(key)
        end_val = start_val + 1  # 2프레임 지정 (예: 220 ~ 221)

        if idx < 8:
            continue        
        cut_number = start_cut_num + idx

        cut_str = str(cut_number).zfill(padding_len)
        
        # 캐릭터 파일명 (예: Fansel_RouletteTitle_CHB_S03-C0110_R00)
        cut_name_char = "%s%sC%s%s" % (base_prefix, separator, cut_str, base_suffix)
        
        # 카메라 파일명 (예: Fansel_RouletteTitle_CHB_S03-C0110_CAM_R00)
        # base_suffix (_R00) 앞에 _CAM을 삽입합니다.
        cut_name_cam = "%s%sC%s_CAM%s" % (base_prefix, separator, cut_str, base_suffix)
        
        cuts.append({
            "name_char": cut_name_char,
            "name_cam": cut_name_cam,
            "start": start_val,
            "end": end_val
        })
        
    print("Planned cuts to export:")
    for cut in cuts:
        print("  - Character: %s" % cut["name_char"])
        print("  - Camera   : %s (Frames: %d ~ %d)" % (cut["name_cam"], cut["start"], cut["end"]))

    # 6. FBX 플러그인 로드 검사
    if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
        cmds.loadPlugin('fbxmaya')
        
    # 7. 공통 FBX 내보내기 설정 (이미지 옵션 기준)
    try:
        mel.eval("FBXResetExport;")
        mel.eval("FBXExportScaleFactor 1;")
        mel.eval("FBXExportShapes -v true;")
        mel.eval("FBXExportSkins -v true;")
        mel.eval("FBXExportInputConnections -v true;")  # Input Connections: Checked
        mel.eval("FBXExportAnimationOnly -v false;")
        mel.eval("FBXExportConstraints -v false;")
        mel.eval("FBXExportCameras -v true;")
        mel.eval("FBXExportLights -v false;")
        mel.eval("FBXExportEmbeddedTextures -v true;")  # Embed Media: Checked
        mel.eval("FBXExportUpAxis y;")                 # Up Axis: Y
        mel.eval("FBXExportInAscii -v 0;")             # File Type: Binary
        mel.eval("FBXExportFileVersion -v FBX202000;") # FBX Version: FBX 2020
        mel.eval("FBXProperty Export|IncludeGrp|Geometry|NurbsCurves -v 0;")  # Export Curves: Unchecked
    except Exception as e:
        cmds.warning("FBX Configuration Error (ignoring): %s" % e)
    
    # 익스포트 대상 지정 (오브젝트 이름, 접미사)
    export_targets = [
        {"node": "root", "suffix": ""},
        {"node": "CAM", "suffix": "_CAM"}
    ]
    
    exported_files = []
    
    # 현재 재생 타임라인 정보 저장
    orig_min = cmds.playbackOptions(q=True, minTime=True)
    orig_max = cmds.playbackOptions(q=True, maxTime=True)
    orig_ast = cmds.playbackOptions(q=True, animationStartTime=True)
    orig_aet = cmds.playbackOptions(q=True, animationEndTime=True)
    
    # Undo 상태 확인 및 강제 활성화
    undo_state = cmds.undoInfo(q=True, state=True)
    if not undo_state:
        cmds.undoInfo(state=True)
        
    # 뷰포트 업데이트 비활성화로 퍼포먼스 최적화
    cmds.refresh(suspend=True)
    try:
        for cut in cuts:
            start_frame = cut["start"]
            end_frame = cut["end"]
            
            print("\nProcessing Cut Range: %d ~ %d" % (start_frame, end_frame))
            
            # 필요한 경우에만 타임라인 강제 변경
            changed_timeline = False
            if orig_min != start_frame or orig_max != end_frame:
                cmds.playbackOptions(minTime=start_frame, maxTime=end_frame)
                changed_timeline = True
            if orig_ast != start_frame or orig_aet != end_frame:
                cmds.playbackOptions(animationStartTime=start_frame, animationEndTime=end_frame)
                changed_timeline = True
                
            for target in export_targets:
                node = target["node"]
                suffix = target["suffix"]
                
                if not cmds.objExists(node):
                    cmds.warning("Object '%s' does not exist." % node)
                    continue
                
                # 파일 이름을 동적으로 지정 (CAM의 경우 컷과 리비전 접미사 사이에 _CAM을 삽입)
                if node == "root":
                    export_name = cut["name_char"]
                elif node == "CAM":
                    export_name = cut["name_cam"]
                else:
                    export_name = cut["name_char"] + suffix
                    
                export_path = "%s/%s.fbx" % (scene_dir.rstrip('/'), export_name)
                
                # 베이크 프레임 지정 (Bake Animation: Checked)
                mel.eval("FBXExportBakeComplexAnimation -v true;")
                mel.eval("FBXExportBakeComplexStart -v %d;" % start_frame)
                mel.eval("FBXExportBakeComplexEnd -v %d;" % end_frame)
                mel.eval("FBXExportBakeComplexStep -v 1;")
                mel.eval("FBXExportBakeResampleAnimation -v true;")
                
                # 익스포트 셀렉션 정의
                export_sel = [node]
                
                # Export Only Joints가 선택되었으므로 root 밑은 조인트만 추출
                if node == "root":
                    joints = cmds.listRelatives(node, type='joint', ad=True, fullPath=True) or []
                    if cmds.objectType(node) == 'joint':
                        joints.append(node)
                    if joints:
                        export_sel = joints
                        
                cmds.select(export_sel, r=True)
                
                # Undo를 이용해 범위 밖 키 일시 삭제
                cmds.undoInfo(openChunk=True)
                try:
                    cmds.cutKey(export_sel, time=(-999999, start_frame - 1))
                    cmds.cutKey(export_sel, time=(end_frame + 1, 999999))
                    
                    # FBX 익스포트 실행
                    mel.eval('FBXExport -f "%s" -s' % export_path)
                    exported_files.append(export_path)
                    print("  - Exported target %s: %s" % (node, export_path))
                except Exception as e:
                    cmds.warning("  - Failed to export target %s: %s" % (node, e))
                finally:
                    cmds.undoInfo(closeChunk=True)
                    cmds.undo()
                    
    finally:
        # 원본 타임라인 복원
        cmds.playbackOptions(minTime=orig_min, maxTime=orig_max)
        cmds.playbackOptions(animationStartTime=orig_ast, animationEndTime=orig_aet)
        
        # 뷰포트 복원
        cmds.refresh(suspend=False)
        
        if not undo_state:
            cmds.undoInfo(state=False)
            
    if exported_files:
        print("\n>>> All FBX Cut Exports Done Successfully. <<<")
        for f in exported_files:
            print("Saved path: %s" % f)

if __name__ == '__main__':
    run_export()
