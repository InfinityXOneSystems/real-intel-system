from bootstrap.health import readiness
from bootstrap.register import register_all


def start():
    register_all()
    return readiness()


if __name__ == "__main__":
    print(start())
