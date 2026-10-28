"""REMADE main entry point. Default: live camera monitoring; --sort enables motion."""

from remade.robot import read_tcp_pose


def main(argv=None):
    from remade.app import main as run
    return run(argv)


if __name__ == '__main__':
    raise SystemExit(main())
