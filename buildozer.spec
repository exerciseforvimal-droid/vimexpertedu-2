[app]
title = Expertedu Attendance
package.name = attendanceapp
package.domain = org.vimal
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 1.0

# Requirements: KivyMD hata diya hai taaki build fast aur stable ho
requirements = python3,kivy==2.3.0

orientation = portrait
fullscreen = 0

# Android specific
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# Architecture: Sirf ye ek rakhein, error nahi aayega
android.archs = armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
