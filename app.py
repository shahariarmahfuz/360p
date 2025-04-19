import os
import subprocess
import threading
import time
import requests
from flask import Flask, render_template_string, send_from_directory, abort

# --- Configuration ---
VIDEO_URLS = [
    "https://video-lax3-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQM79nG_yaRMFQn3uqwDQYldbpHeswPjEw_--HtLuooCdTJabFO_1u-JLVNX_ZThIb6IfOAAcROQ8nrrt_4ZdoJj.mp4?strext=1&_nc_cat=110&_nc_sid=8bf8fe&_nc_ht=video-lax3-1.xx.fbcdn.net&_nc_ohc=YMPB_YdW03QQ7kNvwGGVjqT&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNjQwLnN2ZV9zZCIsInhwdl9hc3NldF9pZCI6MTEwMjgxMzgwODI0NDI3MywidmlfdXNlY2FzZV9pZCI6MTAxMjIsImR1cmF0aW9uX3MiOjIwNiwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_zt=28&oh=00_AfERWi8M9NOZb7bMNyQ8hcvg3WRqmjudXhQMlsVh_LJmSw&oe=680932A4&dl=1",  # প্রথম ভিডিওর URL দিন
    "https://video-fra5-2.xx.fbcdn.net/o1/v/t2/f2/m69/AQOTfyVVjo3KcxyTsTt4akQgRL08sEABNsb80aJfeDyjSIA7MFg7IVuaagNO7Wd3C0DRcI3Soti7lw9V8QSqMiE3.mp4?strext=1&_nc_cat=107&_nc_sid=8bf8fe&_nc_ht=video-fra5-2.xx.fbcdn.net&_nc_ohc=BqX0YpyEauAQ7kNvwHZBI3C&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNjQwLnN2ZV9zZCIsInhwdl9hc3NldF9pZCI6MTMyODc0OTExMTY2MDQwNiwidmlfdXNlY2FzZV9pZCI6MTAxMjIsImR1cmF0aW9uX3MiOjEyNTYsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&_nc_zt=28&oh=00_AfEDTu9FDf3PRWyl73cYxJ7L3nPTfVOMHX6368eJSTPBJg&oe=6809636F&dl=1",  # দ্বিতীয় ভিডিওর URL দিন
    "https://video-lax3-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQM79nG_yaRMFQn3uqwDQYldbpHeswPjEw_--HtLuooCdTJabFO_1u-JLVNX_ZThIb6IfOAAcROQ8nrrt_4ZdoJj.mp4?strext=1&_nc_cat=110&_nc_sid=8bf8fe&_nc_ht=video-lax3-1.xx.fbcdn.net&_nc_ohc=YMPB_YdW03QQ7kNvwGGVjqT&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNjQwLnN2ZV9zZCIsInhwdl9hc3NldF9pZCI6MTEwMjgxMzgwODI0NDI3MywidmlfdXNlY2FzZV9pZCI6MTAxMjIsImR1cmF0aW9uX3MiOjIwNiwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_zt=28&oh=00_AfERWi8M9NOZb7bMNyQ8hcvg3WRqmjudXhQMlsVh_LJmSw&oe=680932A4&dl=1",  # তৃতীয় ভিডিওর URL দিন
    "https://video-fra5-2.xx.fbcdn.net/o1/v/t2/f2/m69/AQOTfyVVjo3KcxyTsTt4akQgRL08sEABNsb80aJfeDyjSIA7MFg7IVuaagNO7Wd3C0DRcI3Soti7lw9V8QSqMiE3.mp4?strext=1&_nc_cat=107&_nc_sid=8bf8fe&_nc_ht=video-fra5-2.xx.fbcdn.net&_nc_ohc=BqX0YpyEauAQ7kNvwHZBI3C&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNjQwLnN2ZV9zZCIsInhwdl9hc3NldF9pZCI6MTMyODc0OTExMTY2MDQwNiwidmlfdXNlY2FzZV9pZCI6MTAxMjIsImR1cmF0aW9uX3MiOjEyNTYsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&_nc_zt=28&oh=00_AfEDTu9FDf3PRWyl73cYxJ7L3nPTfVOMHX6368eJSTPBJg&oe=6809636F&dl=1",  # চতুর্থ ভিডিওর URL দিন
    "https://video-lax3-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQM79nG_yaRMFQn3uqwDQYldbpHeswPjEw_--HtLuooCdTJabFO_1u-JLVNX_ZThIb6IfOAAcROQ8nrrt_4ZdoJj.mp4?strext=1&_nc_cat=110&_nc_sid=8bf8fe&_nc_ht=video-lax3-1.xx.fbcdn.net&_nc_ohc=YMPB_YdW03QQ7kNvwGGVjqT&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNjQwLnN2ZV9zZCIsInhwdl9hc3NldF9pZCI6MTEwMjgxMzgwODI0NDI3MywidmlfdXNlY2FzZV9pZCI6MTAxMjIsImR1cmF0aW9uX3MiOjIwNiwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&_nc_zt=28&oh=00_AfERWi8M9NOZb7bMNyQ8hcvg3WRqmjudXhQMlsVh_LJmSw&oe=680932A4&dl=1"   # পঞ্চম ভিডিওর URL দিন
    # প্রয়োজনে আরও URL যোগ করুন
]
VIDEO_FOLDER = "videos"  # ভিডিও ডাউনলোড করার ফোল্ডার
HLS_FOLDER = "hls"      # HLS স্ট্রিম ফাইল রাখার ফোল্ডার
FFMPEG_PATH = "ffmpeg"  # ffmpeg এর পাথ (Docker এ সাধারণত শুধু নামই যথেষ্ট)
SEGMENT_TIME = 4        # HLS সেগমেন্টের দৈর্ঘ্য (সেকেন্ড)
PLAYLIST_LENGTH = 5     # প্লেলিস্টে কতগুলো সেগমেন্ট রাখা হবে

# --- Flask App Setup ---
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # ব্রাউজার ক্যাশিং বন্ধ করতে

# গ্লোবাল ভেরিয়েবল ffmpeg প্রসেস ট্র্যাক করার জন্য
ffmpeg_process = None
ffmpeg_thread = None
stop_ffmpeg_event = threading.Event()

# --- Helper Functions ---

def create_directories():
    """প্রয়োজনীয় ফোল্ডার তৈরি করে"""
    os.makedirs(VIDEO_FOLDER, exist_ok=True)
    os.makedirs(HLS_FOLDER, exist_ok=True)

def download_video(url, filepath):
    """একটি ভিডিও URL থেকে ডাউনলোড করে"""
    print(f"Downloading {url} to {filepath}...")
    try:
        response = requests.get(url, stream=True, timeout=300) # টাইমআউট যোগ করা হল
        response.raise_for_status()  # HTTP error থাকলে exception raise করবে
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {filepath}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        # যদি ফাইল আংশিক ডাউনলোড হয়ে থাকে, সেটা মুছে ফেলা ভাল
        if os.path.exists(filepath):
            os.remove(filepath)
        return False
    except Exception as e:
        print(f"An unexpected error occurred during download of {url}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False


def download_all_videos():
    """সবগুলো ভিডিও ডাউনলোড করে এবং ফাইলের পাথ লিস্ট রিটার্ন করে"""
    downloaded_files = []
    create_directories()
    for i, url in enumerate(VIDEO_URLS):
        # ফাইলের নাম URL থেকে অনুমান করার চেষ্টা করা বা একটি জেনেরিক নাম দেওয়া
        try:
            filename = url.split('/')[-1].split('?')[0] # URL থেকে ফাইলের নাম বের করার চেষ্টা
            if not filename or '.' not in filename: # যদি নাম না পাওয়া যায় বা এক্সটেনশন না থাকে
                 filename = f"video_{i+1}.mp4" # একটি জেনেরিক নাম দিন
        except Exception:
             filename = f"video_{i+1}.mp4"

        filepath = os.path.join(VIDEO_FOLDER, filename)

        # যদি ফাইল আগে থেকে না থাকে তবেই ডাউনলোড করুন
        if not os.path.exists(filepath):
            if not download_video(url, filepath):
                 print(f"Skipping {url} due to download error.")
                 continue # ডাউনলোড ফেইল করলে পরেরটায় যাও
        else:
            print(f"Video {filepath} already exists. Skipping download.")

        # ডাউনলোড সফল হলে বা আগে থেকেই থাকলে লিস্টে যোগ করুন
        if os.path.exists(filepath):
             downloaded_files.append(filepath)

    if not downloaded_files:
        print("Error: No videos could be downloaded or found. Streaming cannot start.")
        return None

    return downloaded_files

def create_ffmpeg_playlist(video_files):
    """FFmpeg এর জন্য কনক্যাটেনেশন প্লেলিস্ট ফাইল তৈরি করে"""
    playlist_path = os.path.join(VIDEO_FOLDER, "playlist.txt")
    with open(playlist_path, "w", encoding='utf-8') as f:
        for video_file in video_files:
            # ফাইলের পাথে স্পেশাল ক্যারেক্টার থাকলে সমস্যা হতে পারে, তাই quote করা হচ্ছে
            # pathlib ব্যবহার করলে এটি আরও সহজ হতে পারে, কিন্তু os.path দিয়েও কাজ চালানো যায়
            # single quote ব্যবহার করা যাক ffmpeg এর জন্য
            # উইন্ডোজে পাথ সেপারেটর '\' কে '/' দিয়ে বদলানো ভালো
            safe_path = video_file.replace('\\', '/')
            f.write(f"file '{safe_path}'\n")
    return playlist_path

def run_ffmpeg(playlist_path):
    """FFmpeg চালিয়ে HLS স্ট্রিম তৈরি করে"""
    global ffmpeg_process
    hls_output = os.path.join(HLS_FOLDER, "stream.m3u8")

    # পুরানো HLS ফাইল মুছে ফেলা (যদি থাকে)
    if os.path.exists(HLS_FOLDER):
        for filename in os.listdir(HLS_FOLDER):
            file_path = os.path.join(HLS_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error deleting old HLS file {file_path}: {e}")

    # FFmpeg কমান্ড তৈরি
    # -re: নেটিভ ফ্রেমরেটে পড়ার চেষ্টা করে (লাইভ সিমুলেশনের জন্য গুরুত্বপূর্ণ)
    # -fflags +genpts: PTS (Presentation Timestamp) জেনারেট করে যদি ইনপুটে না থাকে
    # -stream_loop -1: ইনপুট ফাইলগুলো শেষ হলে আবার প্রথম থেকে শুরু করবে (concat demuxer এর সাথে)
    # -c copy: যদি সম্ভব হয় ভিডিও/অডিও কোডেক কপি করবে (দ্রুততর), এনকোডিং প্রয়োজন হলে এটি পরিবর্তন করতে হবে (যেমন: -c:v libx264 -c:a aac)
    # -hls_flags delete_segments: পুরনো সেগমেন্ট ডিলিট করবে
    # -hls_time: সেগমেন্টের দৈর্ঘ্য
    # -hls_list_size: প্লেলিস্টে কতগুলো সেগমেন্টের এন্ট্রি থাকবে
    command = [
        FFMPEG_PATH,
        '-re',                   # রিয়েল টাইমে পড়ার চেষ্টা
        '-fflags', '+genpts',    # টাইমস্ট্যাম্প জেনারেট করা
        '-stream_loop', '-1',    # কনক্যাটেনেশন করা ফাইলগুলো লুপ করবে
        '-f', 'concat',          # কনক্যাটেনেশন ফরম্যাট ব্যবহার করা
        '-safe', '0',            # অনিরাপদ ফাইল নেম (যেমন 절대 পাথ) ব্যবহারের অনুমতি
        '-i', playlist_path,     # ইনপুট প্লেলিস্ট ফাইল
        # '-c', 'copy',            # কোডেক কপি করার চেষ্টা (যদি সম্ভব না হয়, এনকোড করতে হবে)
        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', # ভিডিও এনকোডিং (যদি দরকার হয়)
        '-c:a', 'aac', '-b:a', '128k', # অডিও এনকোডিং (যদি দরকার হয়)
        '-f', 'hls',             # আউটপুট ফরম্যাট HLS
        '-hls_time', str(SEGMENT_TIME),        # সেগমেন্টের দৈর্ঘ্য
        '-hls_list_size', str(PLAYLIST_LENGTH), # প্লেলিস্টের সাইজ
        '-hls_flags', 'delete_segments+independent_segments', # পুরনো সেগমেন্ট ডিলিট করা এবং সেগমেন্ট স্বাধীন করা
        '-hls_segment_filename', os.path.join(HLS_FOLDER, 'segment%03d.ts'), # সেগমেন্ট ফাইলের নাম
        hls_output               # মাস্টার প্লেলিস্ট ফাইলের আউটপুট পাথ
    ]

    print("Starting FFmpeg process...")
    print(f"Command: {' '.join(command)}") # কমান্ডটি প্রিন্ট করা

    # subprocess.PIPE ব্যবহার করে আউটপুট ক্যাপচার করা যেতে পারে ডিবাগিং এর জন্য
    # stdin=subprocess.DEVNULL ব্যবহার করা হচ্ছে যাতে ffmpeg কোনো ইনপুটের জন্য অপেক্ষা না করে
    ffmpeg_process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # FFmpeg এর আউটপুট পড়ার জন্য আলাদা থ্রেড (ঐচ্ছিক, ডিবাগিং এর জন্য)
    def log_output(pipe, pipe_name):
        try:
            # পাইপ থেকে UTF-8 হিসাবে ডিকোড করার চেষ্টা করুন, যদি ব্যর্থ হয় তাহলে বাইট হিসাবে লগ করুন
            for line in iter(pipe.readline, b''):
                 try:
                     print(f"FFmpeg {pipe_name}: {line.decode('utf-8').strip()}")
                 except UnicodeDecodeError:
                     print(f"FFmpeg {pipe_name} (bytes): {line.strip()}")
                 if stop_ffmpeg_event.is_set():
                     break
        except Exception as e:
             print(f"Error reading FFmpeg {pipe_name}: {e}")
        finally:
             pipe.close()


    stdout_thread = threading.Thread(target=log_output, args=(ffmpeg_process.stdout, "stdout"))
    stderr_thread = threading.Thread(target=log_output, args=(ffmpeg_process.stderr, "stderr"))
    stdout_thread.start()
    stderr_thread.start()

    # FFmpeg প্রসেস শেষ হওয়ার জন্য অপেক্ষা করা (যদি প্রয়োজন হয়)
    # এখানে আমরা অপেক্ষা করবো না কারণ এটি একটি দীর্ঘস্থায়ী প্রক্রিয়া হবে
    # পরিবর্তে, আমরা এটিকে ব্যাকগ্রাউন্ডে চলতে দেব এবং প্রয়োজনে বন্ধ করব

    # অপেক্ষা করা এবং চেক করা যে প্রসেস চলছে কিনা
    while not stop_ffmpeg_event.is_set():
        if ffmpeg_process.poll() is not None: # প্রসেস কি শেষ হয়ে গেছে?
            print(f"FFmpeg process terminated unexpectedly with code {ffmpeg_process.returncode}.")
            # এখানে রিস্টার্ট করার লজিক যোগ করা যেতে পারে
            break
        time.sleep(1) # কিছুক্ষণ পর পর চেক করা

    print("FFmpeg runner thread finished.")
    # থ্রেড শেষ হলে লগিং থ্রেডগুলোও শেষ হয়েছে নিশ্চিত করা
    stdout_thread.join(timeout=2)
    stderr_thread.join(timeout=2)


def start_streaming_process():
    """ভিডিও ডাউনলোড করে এবং FFmpeg স্ট্রিম শুরু করে"""
    global ffmpeg_thread
    print("Attempting to start streaming process...")
    video_files = download_all_videos()
    if not video_files:
        print("Could not download any videos. Aborting stream start.")
        return False

    playlist_path = create_ffmpeg_playlist(video_files)
    if not playlist_path:
        print("Could not create playlist file. Aborting stream start.")
        return False

    # যদি আগে থেকেই কোনো FFmpeg থ্রেড চলে, তবে এটিকে থামানোর চেষ্টা করুন
    stop_streaming_process()

    # নতুন FFmpeg প্রসেস শুরু করার জন্য থ্রেড তৈরি করুন
    stop_ffmpeg_event.clear() # ইভেন্ট রিসেট করুন
    ffmpeg_thread = threading.Thread(target=run_ffmpeg, args=(playlist_path,), daemon=True)
    ffmpeg_thread.start()
    print("FFmpeg streaming thread started.")
    # স্ট্রীম শুরু হওয়ার জন্য কিছুক্ষণ অপেক্ষা করা যেতে পারে
    time.sleep(5) # যেমন ৫ সেকেন্ড
    # চেক করা যাক HLS ফাইল তৈরি হয়েছে কিনা
    if not os.path.exists(os.path.join(HLS_FOLDER, "stream.m3u8")):
         print("Warning: HLS manifest file not found after starting FFmpeg. Stream might not be ready.")
         # এখানে আরও শক্তিশালী চেকিং যোগ করা যেতে পারে
    else:
         print("HLS manifest file found. Stream should be accessible.")
    return True


def stop_streaming_process():
    """চলমান FFmpeg প্রসেস এবং থ্রেড বন্ধ করে"""
    global ffmpeg_process, ffmpeg_thread
    if ffmpeg_process and ffmpeg_process.poll() is None: # যদি প্রসেস থাকে এবং চলছে
        print("Stopping existing FFmpeg process...")
        stop_ffmpeg_event.set() # থ্রেডকে থামার সিগন্যাল দিন
        try:
            ffmpeg_process.terminate() # প্রথমে টার্মিনেট করার চেষ্টা
            ffmpeg_process.wait(timeout=5) # ৫ সেকেন্ড অপেক্ষা
            print("FFmpeg process terminated.")
        except subprocess.TimeoutExpired:
            print("FFmpeg process did not terminate gracefully, killing...")
            ffmpeg_process.kill() # যদি না হয় তবে কিল করুন
            ffmpeg_process.wait() # নিশ্চিত করুন এটি বন্ধ হয়েছে
            print("FFmpeg process killed.")
        except Exception as e:
            print(f"Error stopping FFmpeg process: {e}")
        ffmpeg_process = None

    if ffmpeg_thread and ffmpeg_thread.is_alive():
         print("Waiting for FFmpeg thread to finish...")
         ffmpeg_thread.join(timeout=10) # থ্রেড শেষ হওয়ার জন্য অপেক্ষা
         if ffmpeg_thread.is_alive():
             print("FFmpeg thread did not finish cleanly.")
         else:
             print("FFmpeg thread finished.")
         ffmpeg_thread = None
    stop_ffmpeg_event.clear() # ইভেন্ট রিসেট করুন


# --- Flask Routes ---

@app.route('/')
def index():
    """HTML পেজ দেখায় যেখানে ভিডিও প্লেয়ার থাকবে"""
    # নিশ্চিত করুন যে 스트িম চলছে
    if ffmpeg_thread is None or not ffmpeg_thread.is_alive():
         print("FFmpeg thread is not running. Attempting to start stream for request.")
         if not start_streaming_process():
              return "Error: Could not start the video stream. Check logs.", 500


    # HLS.js ব্যবহার করে একটি সাধারণ HTML পেজ
    # বিকল্প: Video.js ব্যবহার করা যেতে পারে
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Channel</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body { margin: 0; background-color: #000; }
            video { width: 100%; height: 100vh; }
        </style>
    </head>
    <body>
        <video id="video" controls autoplay muted></video>
        <script>
            var video = document.getElementById('video');
            var hlsUrl = '/hls/stream.m3u8'; // আমাদের HLS স্ট্রিমের URL

            // প্রথমে চেক করুন ব্রাউজার নিজে HLS সাপোর্ট করে কিনা
            if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = hlsUrl;
                video.addEventListener('loadedmetadata', function() {
                    // Autoplay করার চেষ্টা করুন, Muted থাকা অবস্থায় সাধারণত কাজ করে
                    video.play().catch(e => console.error("Autoplay failed:", e));
                });
                console.log("Using native HLS support.");
            }
            // যদি না করে, এবং Hls.js লোড হয়ে থাকে, তবে Hls.js ব্যবহার করুন
            else if (Hls.isSupported()) {
                var hls = new Hls({
                     // প্রয়োজন অনুযায়ী HLS.js কনফিগারেশন যোগ করুন
                     // যেমন, লাইভ স্ট্রিমের জন্য কিছু ডিফল্ট ভ্যালু পরিবর্তন করা লাগতে পারে
                     liveSyncDurationCount: 3, // কতগুলো সেগমেন্ট ধরে লাইভ এজ এর সাথে সিনক্রোনাইজ করার চেষ্টা করবে
                     liveMaxLatencyDurationCount: 5 // কতগুলো সেগমেন্ট পর্যন্ত ল্যাটেন্সি গ্রহণ করবে
                });
                hls.loadSource(hlsUrl);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function() {
                    console.log("HLS.js manifest parsed.");
                    // Autoplay করার চেষ্টা করুন
                    video.play().catch(e => console.error("Autoplay failed:", e));
                });
                hls.on(Hls.Events.ERROR, function(event, data) {
                    console.error('HLS.js error:', data);
                    // এখানে এরর হ্যান্ডলিং যোগ করা যেতে পারে, যেমন স্ট্রিম রিলোড করার চেষ্টা
                    if (data.fatal) {
                        switch(data.type) {
                            case Hls.ErrorTypes.NETWORK_ERROR:
                                console.log("Fatal network error encountered, trying to recover...");
                                hls.startLoad(); // আবার লোড করার চেষ্টা
                                break;
                            case Hls.ErrorTypes.MEDIA_ERROR:
                                console.log("Fatal media error encountered, trying to recover...");
                                hls.recoverMediaError();
                                break;
                            default:
                                // আনরিকভারেবল এরর, hls destroy করা হতে পারে
                                console.log("Unrecoverable HLS error, destroying HLS instance.");
                                hls.destroy();
                                break;
                        }
                    }
                });
                 console.log("Using HLS.js for playback.");
            } else {
                alert("Sorry, your browser does not support HLS playback.");
            }

            // ভিডিও আনমিউট করার জন্য একটি বাটন যোগ করা যেতে পারে কারণ অনেক ব্রাউজার অটো প্লে মিউট ছাড়া করতে দেয় না
            // document.body.addEventListener('click', () => { video.muted = false; }, { once: true });

        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/hls/<path:filename>')
def hls_files(filename):
    """HLS প্লেলিস্ট (.m3u8) এবং সেগমেন্ট (.ts) ফাইল পরিবেশন করে"""
    hls_dir = os.path.abspath(HLS_FOLDER)
    try:
        # send_from_directory ব্যবহার করে নিরাপদভাবে ফাইল পরিবেশন করা
        # Cache কন্ট্রোল হেডার যোগ করা যাতে ব্রাউজার সবসময় নতুন ফাইল নেয়
        response = send_from_directory(hls_dir, filename)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except FileNotFoundError:
        print(f"HLS file not found: {filename}")
        abort(404)
    except Exception as e:
        print(f"Error serving HLS file {filename}: {e}")
        abort(500)


# --- Main Execution ---
if __name__ == '__main__':
    # অ্যাপ শুরু হওয়ার সময় একবার স্ট্রিম চালু করার চেষ্টা করুন
    if not start_streaming_process():
         print("Failed to start initial streaming process. The server will run, but the stream might not be available until manually triggered or restarted.")
         # আপনি এখানে অ্যাপ বন্ধ করে দিতে পারেন যদি স্ট্রিম শুরু না হলে চালানোর মানে না থাকে
         # import sys
         # sys.exit(1)

    # Flask অ্যাপটি 0.0.0.0 তে রান করানো হচ্ছে যাতে Docker কন্টেইনারের বাইরে থেকেও অ্যাক্সেস করা যায়
    # debug=False ব্যবহার করা উচিত প্রোডাকশনের জন্য বা যখন ব্যাকগ্রাউন্ড থ্রেড ব্যবহার করা হচ্ছে
    # use_reloader=False ব্যবহার করা গুরুত্বপূর্ণ যখন ব্যাকগ্রাউন্ড থ্রেড বা প্রসেস চালানো হচ্ছে,
    # কারণ রিলোডার অ্যাপটি দুইবার চালু করতে পারে বা থ্রেড ব্যবস্থাপনায় সমস্যা করতে পারে।
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

    # অ্যাপ বন্ধ হওয়ার সময় FFmpeg প্রসেস বন্ধ করার চেষ্টা করা (যদিও এটি সবসময় কাজ নাও করতে পারে)
    # @atexit মডিউল ব্যবহার করা যেতে পারে অথবা ম্যানুয়ালি সিগন্যাল হ্যান্ডেল করা যেতে পারে
    import atexit
    atexit.register(stop_streaming_process)
