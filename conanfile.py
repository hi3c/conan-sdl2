from conans import ConanFile, CMake, tools
import os


class SdlConan(ConanFile):
    name = "SDL2"
    version = "2.0.5_1"
    license = "<Put the package license here>"
    url = "<Package recipe repository url here, for issues about the package>"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    options = {"sdlmain": [True, False]}
    default_options = "sdlmain=False"
    requires = "multibuilder/1.0@hi3c/experimental"

    def source(self):
        url = "https://www.libsdl.org/release/SDL2-2.0.5.zip"
        if self.settings.os == "Windows":
            url = "http://libsdl.org/release/SDL2-devel-2.0.5-VC.zip"

        tools.download(url, "SDL.zip")
        tools.unzip("SDL.zip")

    def build(self):
        if self.settings.os == "Windows":
            return

        if self.settings.os == "iOS" and self.settings.arch == "universal":
            # using xcodebuild for this
            projectfile = os.path.join(self.conanfile_directory, "SDL2-2.0.5", "Xcode-iOS", "SDL", "SDL.xcodeproj")
            with tools.environment_append({"CC": "", "CXX": "", "CFLAGS": "", "CXXFLAGS": "", "LDFLAGS": ""}):
              # start with iOS sdk
              self.run("xcodebuild -sdk iphoneos -configuration Release -project {} CONFIGURATION_BUILD_DIR={}".format(projectfile,
                  os.path.join(self.conanfile_directory, "build-iOS")))
              
              # now iphonesimulator
              self.run("xcodebuild -sdk iphonesimulator -configuration Release -project {} CONFIGURATION_BUILD_DIR={}".format(projectfile,
                  os.path.join(self.conanfile_directory, "build-iOSSimulator")))
            
            os.makedirs(os.path.join(self.conanfile_directory, "build-universal"))
            self.run("lipo -output {}/libSDL2.a -create {} {}".format(
                os.path.join(self.conanfile_directory, "build-universal"),
                os.path.join(self.conanfile_directory, "build-iOS", "libSDL2.a"),
                os.path.join(self.conanfile_directory, "build-iOSSimulator", "libSDL2.a")))

    def package(self):
        self.copy("*.h", dst="include", src="SDL2-2.0.5/include")
        self.copy("SDL_config.h", dst="include", src="include")

        if self.settings.os == "Windows":
            archdir = "SDL2-2.0.5/lib/{}".format("x64" if self.settings.arch == "x86_64" else "x86")
            self.copy("SDL2.lib", src=archdir, dst="lib")
            if self.options.sdlmain:
                self.copy("SDL2main.lib", src=archdir, dst="lib")
            self.copy("*.dll", src=archdir, dst="bin")

        self.copy("*.a", dst="lib", src="build-universal", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["SDL2"]
        if self.options.sdlmain and not self.settings.os == "iOS":
            self.cpp_info.libs.append("SDL2main")
        if self.settings.os == "iOS":
            self.cpp_info.sharedlinkflags = ["-framework CoreFoundation",
                                             "-framework CoreAudio",
                                             "-framework OpenGLES",
                                             "-framework AudioToolbox",
                                             "-framework UIKit",
                                             "-framework AVFoundation",
                                             "-framework GameController",
                                             "-framework QuartzCore",
                                             "-framework Foundation",
                                             "-framework CoreMotion",
                                             "-framework CoreGraphics"]
            self.cpp_info.exelinkflags = self.cpp_info.sharedlinkflags
                              
