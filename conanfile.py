import os
from conans import ConanFile, CMake, tools

class TrantorConan(ConanFile):
    name = "drogon"
    version = "1.0.0-beta11"
    license = "MIT"
    author = "Tao An"
    url = "https://github.com/sdmg15/drogon-conan"
    homepage = "https://github.com/an-tao/drogon"
    description = "A C++14/17 based HTTP web application framework running on Linux/macOS/Unix "
    topics = ("non-blocking", "http-server", "http")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    exports_sources = "CMakeLists.txt"

    requires = (
        "zlib/1.2.11",
        "boost/1.71.0@conan/stable",
        "jsoncpp/1.9.0@theirix/stable",
        "libuuid/1.0.3@bincrafters/stable",
        "openssl/1.0.2t",
        "trantor/1.0.0-rc6@trantor/stable",
        "sqlite3/3.14.1@bincrafters/stable",
        "libmysqlclient/8.0.17"
    )

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        sha256 = "33344544b0e4e5b62560e8cefed866f76a61151d66fca444a28d7e7f5c8e89e3"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        # Drogon requires private headers from Trantor
        with tools.chdir(self._source_subfolder):
            git = tools.Git("trantor")
            git.clone("https://github.com/an-tao/trantor.git", "v1.0.0-rc6")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_CTL"] = False
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def _patch(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "add_subdirectory(trantor)", "target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/trantor)")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "PUBLIC trantor)", "PUBLIC ${CONAN_LIBS})")
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"), "FATAL_ERROR", "WARN")
        
    def build(self):
        self._patch()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")