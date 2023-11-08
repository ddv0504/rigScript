import springmagic.py2
import springmagic.py2.ui as ui

def main(*args, **kwargs):

    widget = ui.SpringMagicWidget()
    widget.show()


if __name__ == "__main__":

    with springmagic.app():
        springmagic.main()
