[app]
title = Attendance App
package.name = attendanceapp
package.domain = org.vimal
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
version = 0.1

# Requirements: Kivy aur KivyMD ka stable version set kiya hai
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,sqlite3

orientation = portrait
fullscreen = 0

# Android specific (Inhe dhyan se dekhein)
android.api = 33
android.minapi = 21
# NDK 25b sabse stable hai GitHub Actions ke liye
android.ndk = 27b
android.ndk_path = 
android.sdk_path = 
android.accept_sdk_license = True

# Permissions: Attendance app ke liye zaruri hain
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, CAMERA

# Architecture: Sirf armeabi-v7a rakha hai taaki build fail na ho aur jaldi bane
android.archs = armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
