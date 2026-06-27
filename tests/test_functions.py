from src import add, subtract, multiply,divide


def test_add():
    assert add(2, 3) == 5
    assert  add(10, 100) == 110


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(-1, -3) == 2

def test_multilply():
    assert multiply(2, 5) == 10
    assert multiply(100, 10) == 1000

def test_divide():
    assert divide(3, 4) == 3/4
    assert divide(6, 3) == 2
