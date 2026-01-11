#include <iostream>
#include "string_utils.h"

int main() {
    std::cout << "Hello from CMake project!" << std::endl;
    std::string result = string_utils::uppercase("cmake");
    std::cout << "Uppercase: " << result << std::endl;
    return 0;
}
