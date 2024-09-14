
import time
import pytest

class TestRepeated:
    value = 0

    def setup(self):
        self.value = 0
        print(f"Setting up test {self.value}")

    def teardown(self):
        print(f"Tearing down test {self.value}")
        self.value = None
        time.sleep(1)

    @pytest.fixture
    def my_resource(self):
        self.setup()
        yield
        self.teardown()

    @pytest.mark.repeat(3)
    def test_repeated(self,my_resource):
        self.value += 1
        print(f"Running test iteration, value is {self.value}")
        assert self.value == 1

