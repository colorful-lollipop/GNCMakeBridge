#include <iostream>
#include "string_utils.h"

int main() {
    std::cout << "Hello, World!" << std::endl;
    std::string result = string_utils::uppercase("hello");
    std::cout << "Uppercase: " << result << std::endl;
    return 0;
}
