#ifndef FILE_UTILS_H
#define FILE_UTILS_H

#include <string>

namespace file_utils {
    std::string read_file(const std::string& filename);
    bool write_file(const std::string& filename, const std::string& content);
}

#endif // FILE_UTILS_H
