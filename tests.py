from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content


def test_get_files_info_dotpath_success():
    response = get_files_info("calculator", ".")
    print(f"Result for current directory:\n{response}")


def test_get_files_info_dir_success():
    response = get_files_info("calculator", "pkg")
    print(f"Result for 'pkg' directory:\n{response}")


def test_get_files_info_oob_abspath_failure():
    response = get_files_info("calculator", "/bin")
    print(f"Result for '/bin' directory:\n{response}")


def test_get_files_info_oob_relpath_failure():
    response = get_files_info("calculator", "../")
    print(f"Result for '../' directory:\n{response}")


def test_get_file_content_size_limit_success():
    response = get_file_content("calculator", "lorem.txt")
    print(f"Contents of 'lorem.txt' file:\n{response}")


def test_get_file_content_filename_success():
    response = get_file_content("calculator", "main.py")
    print(f"Contents of 'main.py' file:\n{response}")


def test_get_file_content_relpath_success():
    response = get_file_content("calculator", "pkg/calculator.py")
    print(f"Contents of 'pkg/calculator.py' file:\n{response}")


def test_get_file_content_oob_abspath_failure():
    response = get_file_content("calculator", "/bin/cat")
    print(f"Contents of '/bin/cat' file:\n{response}")


def test_get_file_content_file_not_found_failure():
    response = get_file_content("calculator", "pkg/does_not_exist.py")
    print(f"Contents of 'pkg/does_not_exist.py' file:\n{response}")


def main():
    for func in [
        # test_get_files_info_dotpath_success,
        # test_get_files_info_dir_success,
        # test_get_files_info_oob_abspath_failure,
        # test_get_files_info_oob_relpath_failure,
        # test_get_file_content_size_limit_success,
        test_get_file_content_filename_success,
        test_get_file_content_relpath_success,
        test_get_file_content_oob_abspath_failure,
        test_get_file_content_file_not_found_failure,
    ]:
        func()


if __name__ == "__main__":
    main()
