:: usage: encode-mjpeg-vorbis.bat <input> <video quality> <audio quality> <fps> <output>

:: normalize
ffmpeg -i %1 -c:a copy -preset ultrafast -qp 0 -r %4 tmp-feed.mp4

:: create the mjpeg stream
python mozmjpeg.py -i tmp-feed.mp4 -o mux-video.mjpeg -quality %2

del tmp-feed.mp4

:: extract the audio
ffmpeg -i %1 -c:a libvorbis -q:a %3 mux-audio.ogg

:: combine it all
ffmpeg -framerate %4 -i mux-video.mjpeg -i mux-audio.ogg -c:v copy -c:a copy %5

del mux-video.mjpeg
del mux-audio.ogg

echo [+] all done!