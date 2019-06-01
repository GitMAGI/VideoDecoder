adb -s 07ea9707 push "scrcpy-server.jar" "/data/local/tmp/scrcpy-server.jar"
adb -s 07ea9707 reverse localabstract:scrcpy tcp:27183
adb -s 07ea9707 shell CLASSPATH=/data/local/tmp/scrcpy-server.jar app_process / com.genymobile.scrcpy.Server 0 8000000 false - true
adb -s 07ea9707 reverse --remove localabstract:scrcpy