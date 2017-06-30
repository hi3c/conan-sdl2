from conans import ConanFile, CMake, tools
import os


class SdlConan(ConanFile):
    name = "SDL2"
    version = "2.0.5"
    license = "<Put the package license here>"
    url = "<Package recipe repository url here, for issues about the package>"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    options = {"sdlmain": [True, False]}
    default_options = "sdlmain=False"

    def source(self):
        url = "https://www.libsdl.org/release/SDL2-2.0.5.zip"
        if self.settings.os == "Windows":
            url = "http://libsdl.org/release/SDL2-devel-2.0.5-VC.zip"

        tools.download(url, "SDL.zip")
        tools.unzip("SDL.zip")

    def build_id(self):
        if self.settings.os == "Windows":
            self.info_build.options.sdlmain = "Any"
            self.info_build.settings.arch = "Any"
            self.info_build.settings.build_type = "Any"

    def build(self):
        if self.settings.os == "Windows":
            return

        cmake = CMake(self)
        shared = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else ""
        self.run('cmake SDL2-2.0.5 %s %s' % (cmake.command_line, shared))
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include", src="SDL2-2.0.5/include")
        self.copy("SDL_config.h", dst="include", src="include")

        if self.settings.os == "Windows":
            archdir = "SDL2-2.0.5/lib/{}".format("x64" if self.settings.arch == "x86_64" else "x86")
            self.copy("SDL2.lib", src=archdir, dst="lib")
            if self.options.sdlmain:
                self.copy("SDL2main.lib", src=archdir, dst="lib")
            self.copy("*.dll", src=archdir, dst="bin")

        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["SDL2"]
        if self.options.sdlmain:
            self.cpp_info.libs.append("SDL2main")
