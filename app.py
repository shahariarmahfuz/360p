import os
import subprocess
import threading
import time
import signal
import requests
import re # রেগুলার এক্সপ্রেশন ব্যবহারের জন্য
import collections # deque ব্যবহারের জন্য
from flask import Flask, render_template, send_from_directory, abort
from flask_cors import CORS

# --- কনফিগারেশন ---
VIDEO_LINKS = [
    "https://video-fra3-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQOY4fMfQQNsW-ZUVFXxHTm39PI1pROqwbPofqDUUF1gm8uaZc0dz2pnhDGnEiCl6clsoW_K_t_6ZC-5r-8b51-c.mp4?strext=1&_nc_cat=101&_nc_sid=5e9851&_nc_ht=video-fra3-1.xx.fbcdn.net&_nc_ohc=GdYUyRVIcbgQ7kNvwEip_3Y&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNTc2LmRhc2hfaDI2NC1iYXNpYy1nZW4yXzcyMHAiLCJ4cHZfYXNzZXRfaWQiOjEwNDIyMTg5ODc3NTc2NTEsInZpX3VzZWNhc2VfaWQiOjEwMTIyLCJkdXJhdGlvbl9zIjo2OSwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&vs=723b4f56308343e1&_nc_vs=HBksFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HT2pWT1IzaWtCVUtDbzBEQU1VNHJrMVFPbXNmYm1kakFBQUYVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dDeHNIaDAxRzMtTUoxMENBSi1DYmJGOXJlWXFickZxQUFBRhUCAsgBACgAGAAbAogHdXNlX29pbAExEnByb2dyZXNzaXZlX3JlY2lwZQExFQAAJqaB2ciQ-dkDFQIoAkMzLBdAUXd87ZFocxgZZGFzaF9oMjY0LWJhc2ljLWdlbjJfNzIwcBEAdQIA&_nc_zt=28&oh=00_AfFNaL9V0zY7vP-3hEMLbJWTnsL8CavMenvKug9oJ11W6Q&oe=680994C5&dl=1",
    "https://video-lax3-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQPGDN71PyrUR_izj6iGuJu_PykflRlRdDnXIk_U2uPGiTDpw8JIbvWTzAi31EcxqyQZ2080Y-AWe-kq6ydx4_lP.mp4?strext=1&_nc_cat=108&_nc_sid=5e9851&_nc_ht=video-lax3-1.xx.fbcdn.net&_nc_ohc=dTByeKQDJpwQ7kNvwGTqtPN&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuOTYwLmRhc2hfaDI2NC1iYXNpYy1nZW4yXzcyMHAiLCJ4cHZfYXNzZXRfaWQiOjQ2MDU4MTkyOTk1NDkzMywidmlfdXNlY2FzZV9pZCI6MTAxMjIsImR1cmF0aW9uX3MiOjY4NiwidXJsZ2VuX3NvdXJjZSI6Ind3dyJ9&ccb=17-1&vs=fcbb29a4927b8e91&_nc_vs=HBksFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HQWlsWnh4LWxpWUNHNVFEQUZFck0xdGcyRXdBYm1kakFBQUYVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dBdFRBeHJtX2FqU1MzY0RBT2dCcWV4UXZaeDVidjRHQUFBRhUCAsgBACgAGAAbAogHdXNlX29pbAExEnByb2dyZXNzaXZlX3JlY2lwZQExFQAAJuq5meWyudEBFQIoAkMzLBdAhXOFHrhR7BgZZGFzaF9oMjY0LWJhc2ljLWdlbjJfNzIwcBEAdQIA&_nc_zt=28&oh=00_AfH6U8t1LY-c_kEUA2TbVs-ug57-iKPUhq-B4uijAOfGzA&oe=6809A106&dl=1",
    "https://video-lax3-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQN0DwhCrb_XoX5aX_7RHBX6Jzz-9Z8PCLoOGiSXqDtEXuvTRbi_TmrLZ5SBcAvjpy5tzP9hozjSJi9xtyv8uJqk.mp4?strext=1&_nc_cat=105&_nc_sid=5e9851&_nc_ht=video-lax3-1.xx.fbcdn.net&_nc_ohc=r4oC03xBjUsQ7kNvwFv52YA&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNzIwLmRhc2hfaDI2NC1iYXNpYy1nZW4yXzcyMHAiLCJ4cHZfYXNzZXRfaWQiOjQ1NDE0Mjg5NjA5ODc0MiwiYXNzZXRfYWdlX2RheXMiOjEwMTYsInZpX3VzZWNhc2VfaWQiOjEwMTIyLCJkdXJhdGlvbl9zIjozOTgsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=a5993c3685094af8&_nc_vs=HBksFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HRy1TOFJ3TWppNWx2VVVDQU9SSW8wWmt3cEYxYm1kakFBQUYVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dQXzViaEUzOW53ZVlsQUJBRVdaOWNnb0ZxUlpidjRHQUFBRhUCAsgBACgAGAAbAogHdXNlX29pbAExEnByb2dyZXNzaXZlX3JlY2lwZQExFQAAJuy2_p_Mws4BFQIoAkMzLBdAeOXbItDlYBgZZGFzaF9oMjY0LWJhc2ljLWdlbjJfNzIwcBEAdQIA&_nc_zt=28&oh=00_AfHouaKEQe-HG_i1Mn0bYZEt7EHhdVKJxmnZXo-w0nl3rA&oe=6809A3E1&dl=1",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
    "https://video-gru2-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQNz0zSpUBK5t5pu3JkErharuTv0WRZxvPeoTSGFjDBm_C4t2Or8fdX8xBlQJFq6iiFA4AQ1o2KfbLEnE050MD-f.mp4?strext=1&_nc_cat=107&_nc_sid=5e9851&_nc_ht=video-gru2-1.xx.fbcdn.net&_nc_ohc=MYgestNRyDMQ7kNvwHy_kSX&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuMTE1Mi5kYXNoX2gyNjQtYmFzaWMtZ2VuMl83MjBwIiwieHB2X2Fzc2V0X2lkIjoyNDM0Njc3ODExODI1NTU3NSwidmlfdXNlY2FzZV9pZCI6MTAxMjIsImR1cmF0aW9uX3MiOjI2NzcsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=d717508f1df09c38&_nc_vs=HBksFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HSUNXbUFBM2kweDRXT1FCQUF5RXRWenpzb3BwYm1kakFBQUYVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dQSmlLeDA1eTBadmw2TURBR3l0dWFBNVVjMDVickZxQUFBRhUCAsgBACgAGAAbAogHdXNlX29pbAExEnByb2dyZXNzaXZlX3JlY2lwZQExFQAAJq7Pz9KA0b9WFQIoAkMzLBdApOrul41P3xgZZGFzaF9oMjY0LWJhc2ljLWdlbjJfNzIwcBEAdQIA&_nc_zt=28&oh=00_AfGYFiCWahHFQefIfrywjrqFVM6JoqsFa6HKbY9BBCqI9w&oe=68097553&dl=1",
    "https://video-lax3-1.xx.fbcdn.net/o1/v/t2/f2/m69/AQN0DwhCrb_XoX5aX_7RHBX6Jzz-9Z8PCLoOGiSXqDtEXuvTRbi_TmrLZ5SBcAvjpy5tzP9hozjSJi9xtyv8uJqk.mp4?strext=1&_nc_cat=105&_nc_sid=5e9851&_nc_ht=video-lax3-1.xx.fbcdn.net&_nc_ohc=r4oC03xBjUsQ7kNvwFv52YA&efg=eyJ2ZW5jb2RlX3RhZyI6Inhwdl9wcm9ncmVzc2l2ZS5GQUNFQk9PSy4uQzMuNzIwLmRhc2hfaDI2NC1iYXNpYy1nZW4yXzcyMHAiLCJ4cHZfYXNzZXRfaWQiOjQ1NDE0Mjg5NjA5ODc0MiwiYXNzZXRfYWdlX2RheXMiOjEwMTYsInZpX3VzZWNhc2VfaWQiOjEwMTIyLCJkdXJhdGlvbl9zIjozOTgsInVybGdlbl9zb3VyY2UiOiJ3d3cifQ%3D%3D&ccb=17-1&vs=a5993c3685094af8&_nc_vs=HBksFQIYOnBhc3N0aHJvdWdoX2V2ZXJzdG9yZS9HRy1TOFJ3TWppNWx2VVVDQU9SSW8wWmt3cEYxYm1kakFBQUYVAALIAQAVAhg6cGFzc3Rocm91Z2hfZXZlcnN0b3JlL0dQXzViaEUzOW53ZVlsQUJBRVdaOWNnb0ZxUlpidjRHQUFBRhUCAsgBACgAGAAbAogHdXNlX29pbAExEnByb2dyZXNzaXZlX3JlY2lwZQExFQAAJuy2_p_Mws4BFQIoAkMzLBdAeOXbItDlYBgZZGFzaF9oMjY0LWJhc2ljLWdlbjJfNzIwcBEAdQIA&_nc_zt=28&oh=00_AfHouaKEQe-HG_i1Mn0bYZEt7EHhdVKJxmnZXo-w0nl3rA&oe=6809A3E1&dl=1",
    # "আপনার ভিডিও লিঙ্ক ১",
    # "আপনার ভিডিও লিঙ্ক ২",
    # "আপনার ভিডিও লিঙ্ক ৩",
    # "আপনার ভিডিও লিঙ্ক ৪",
    # "আপনার ভিডিও লিঙ্ক ৫",
]
VIDEO_DIR = "videos"
STREAM_OUTPUT_DIR = "stream_output"
FFMPEG_PLAYLIST_FILE = "playlist.txt"
HLS_OUTPUT_FILE = os.path.join(STREAM_OUTPUT_DIR, "stream.m3u8")
SKIPPED_VIDEOS_FILE = "skipped_videos.json" # বাদ দেওয়া ভিডিওর তালিকা সেভ করার ফাইল

# গ্লোবাল ভেরিয়েবল
downloaded_videos = []
skipped_videos = set() # বাদ দেওয়া ভিডিওর সেট
ffmpeg_process = None
ffmpeg_monitor_thread = None
ffmpeg_stderr_lines = collections.deque(maxlen=50) # FFmpeg এর শেষ কয়েকটি stderr লাইন রাখার জন্য
stop_event = threading.Event()
ffmpeg_restart_lock = threading.Lock() # একই সাথে একাধিক রিস্টার্ট এড়ানোর জন্য

app = Flask(__name__)
CORS(app)

# --- ডিরেক্টরি তৈরি ---
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(STREAM_OUTPUT_DIR, exist_ok=True)

# --- বাদ দেওয়া ভিডিওর তালিকা লোড/সেভ ---
def load_skipped_videos():
    global skipped_videos
    if os.path.exists(SKIPPED_VIDEOS_FILE):
        try:
            with open(SKIPPED_VIDEOS_FILE, "r") as f:
                import json
                skipped_paths = json.load(f)
                skipped_videos = set(skipped_paths)
                print(f"Loaded {len(skipped_videos)} skipped videos from {SKIPPED_VIDEOS_FILE}", flush=True)
        except Exception as e:
            print(f"Error loading skipped videos file: {e}", flush=True)

def save_skipped_videos():
    try:
        with open(SKIPPED_VIDEOS_FILE, "w") as f:
            import json
            json.dump(list(skipped_videos), f)
        # print(f"Saved skipped videos to {SKIPPED_VIDEOS_FILE}", flush=True)
    except Exception as e:
        print(f"Error saving skipped videos file: {e}", flush=True)

# --- FFmpeg প্লেলিস্ট তৈরি (বাদ দেওয়া ভিডিও ছাড়া) ---
def create_ffmpeg_playlist():
    """শুধুমাত্র ডাউনলোড হওয়া এবং বাদ না দেওয়া ভিডিওগুলো দিয়ে playlist.txt তৈরি করে"""
    global skipped_videos
    active_videos = []
    for video_path in downloaded_videos:
        abs_video_path = os.path.abspath(video_path)
        if abs_video_path not in skipped_videos:
            active_videos.append(abs_video_path)

    if not active_videos:
        print("কোনো সক্রিয় ভিডিও নেই (সবগুলো বাদ দেওয়া হতে পারে বা ডাউনলোড হয়নি)। প্লেলিস্ট খালি থাকবে।", flush=True)
        if os.path.exists(FFMPEG_PLAYLIST_FILE):
            try:
                os.remove(FFMPEG_PLAYLIST_FILE)
            except OSError as e:
                print(f"Error removing empty playlist file: {e}", flush=True)
        return False

    try:
        with open(FFMPEG_PLAYLIST_FILE, "w", encoding='utf-8') as f:
            for video_path in active_videos:
                # Ensure path escaping if necessary, though quotes usually handle it
                f.write(f"file '{video_path}'\n")
        print(f"'{FFMPEG_PLAYLIST_FILE}' তৈরি/আপডেট হয়েছে {len(active_videos)} টি সক্রিয় ভিডিও দিয়ে।", flush=True)
        return True
    except Exception as e:
        print(f"প্লেলিস্ট ফাইল লিখতে ত্রুটি: {e}", flush=True)
        return False


# --- FFmpeg stderr মনিটর ---
def monitor_ffmpeg_stderr(process, stop_flag):
    """FFmpeg এর stderr পড়ে এবং শেষ লাইনগুলো সংরক্ষণ করে"""
    global ffmpeg_stderr_lines
    print("FFmpeg stderr মনিটর থ্রেড চালু হয়েছে।", flush=True)
    if process and process.stderr:
        try:
            # Use process.stderr directly as an iterator
            for line_bytes in process.stderr:
                 if stop_flag.is_set():
                      print("Stderr মনিটর থ্রেড বন্ধ করার সিগন্যাল পেয়েছে।", flush=True)
                      break
                 try:
                      decoded_line = line_bytes.decode('utf-8', errors='replace').strip()
                      if decoded_line:
                          # print(f"FFmpeg stderr: {decoded_line}", flush=True) # এটি খুব বেশি আউটপুট দিতে পারে
                          ffmpeg_stderr_lines.append(decoded_line)
                 except Exception as decode_err:
                      print(f"Stderr লাইন ডিকোড করতে ত্রুটি: {decode_err}", flush=True)
                      ffmpeg_stderr_lines.append(f"[DECODE ERROR] {line_bytes}")

            # Ensure the stderr pipe is closed after reading finishes or stop is signalled
            if not process.stderr.closed:
                process.stderr.close()
        except Exception as e:
            # This might happen if the process terminates abruptly and the pipe breaks
            print(f"FFmpeg stderr পড়তে গিয়ে ত্রুটি: {e}", flush=True)
        finally:
             # Ensure stderr is closed if loop exits for any reason other than pipe closing itself
            if process and process.stderr and not process.stderr.closed:
                 try:
                     process.stderr.close()
                 except Exception:
                     pass # Ignore errors during cleanup closing
    print("FFmpeg stderr মনিটর থ্রেড শেষ হয়েছে।", flush=True)


# --- FFmpeg স্ট্রিম শুরু/পুনরায় শুরু করা ---
def start_ffmpeg_stream(is_restart=False):
    """বর্তমান প্লেলিস্ট ব্যবহার করে FFmpeg স্ট্রিম শুরু বা পুনরায় শুরু করে"""
    global ffmpeg_process, ffmpeg_monitor_thread

    # একই সাথে একাধিক রিস্টার্ট চেষ্টা এড়ানোর জন্য লক ব্যবহার
    if not ffmpeg_restart_lock.acquire(blocking=False):
         print("অন্য একটি রিস্টার্ট প্রক্রিয়া চলছে, এটি এড়িয়ে যাওয়া হচ্ছে।", flush=True)
         return

    try:
        # যদি আগের FFmpeg প্রসেস চালু থাকে, তবে বন্ধ করুন
        # কিন্তু যদি এটি একটি পরিকল্পিত রিস্টার্ট হয় (যেমন নতুন ভিডিও ডাউনলোডের পর)
        # তাহলে মনিটরিং থ্রেডকে আগে বন্ধ করার সিগন্যাল দিতে হবে
        if ffmpeg_process:
             print("চলমান FFmpeg প্রসেস বন্ধ করা হচ্ছে...", flush=True)
             # মনিটর থ্রেডকে সিগন্যাল দাও বন্ধ হওয়ার জন্য (যদি চালু থাকে)
             if ffmpeg_monitor_thread and ffmpeg_monitor_thread.is_alive():
                  # এই থ্রেডের জন্য একটি স্টপ ফ্ল্যাগ লাগবে
                  # আপাতত সরাসরি বন্ধ করার চেষ্টা করা হচ্ছে, যা আদর্শ নয়
                  pass # Ideally signal the monitor thread to stop cleanly before terminating ffmpeg_process

             stop_ffmpeg_stream(graceful_timeout=2) # ছোট টাইমআউট দিয়ে বন্ধ করার চেষ্টা
             ffmpeg_process = None # নিশ্চিত করুন যে এটি None সেট করা হয়েছে

        # প্লেলিস্ট তৈরি করুন (বাদ দেওয়া ভিডিও ছাড়া)
        if not create_ffmpeg_playlist():
            print("সক্রিয় প্লেলিস্ট তৈরি করা যায়নি, FFmpeg চালু হচ্ছে না।", flush=True)
            return # প্লেলিস্ট খালি থাকলে শুরু করবেনা

        # FFmpeg কমান্ড (আগের মতই)
        ffmpeg_command = [
            'ffmpeg', '-hide_banner', '-loglevel', 'warning', # লগ কমানোর জন্য
            '-re',
            '-f', 'concat',
            '-safe', '0',
            '-i', FFMPEG_PLAYLIST_FILE,
            '-c:v', 'libx264',
            '-preset', 'veryfast', # রিসোর্স অনুযায়ী পরিবর্তন করুন
            '-b:v', '1000k', # রিসোর্স অনুযায়ী পরিবর্তন করুন
            '-maxrate', '1000k',
            '-bufsize', '2000k',
            '-g', '60',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-vf', 'scale=640:360',
            '-f', 'hls',
            '-hls_time', '4',
            '-hls_list_size', '5',
            '-hls_flags', 'delete_segments+omit_endlist',
            '-hls_segment_filename', os.path.join(STREAM_OUTPUT_DIR, 'segment%03d.ts'),
            HLS_OUTPUT_FILE
        ]

        print("FFmpeg কমান্ড:", " ".join(ffmpeg_command), flush=True)
        try:
            # stderr পাইপ করুন যাতে মনিটর করা যায়
            ffmpeg_process = subprocess.Popen(ffmpeg_command, stderr=subprocess.PIPE)
            print(f"FFmpeg প্রসেস শুরু হয়েছে (PID: {ffmpeg_process.pid})", flush=True)

            # stderr মনিটর থ্রেড শুরু করুন (নতুন প্রসেসের জন্য)
            # একটি স্টপ ফ্ল্যাগ তৈরি করুন যা এই থ্রেডকে বাইরে থেকে বন্ধ করার সিগন্যাল দিতে পারে
            # আপাতত, থ্রেডটি প্রসেস শেষ না হওয়া পর্যন্ত চলবে বা এরর না দেওয়া পর্যন্ত
            stderr_stop_flag = threading.Event() # এই ফ্ল্যাগটি ম্যানেজ করতে হবে
            ffmpeg_monitor_thread = threading.Thread(target=monitor_ffmpeg_stderr, args=(ffmpeg_process, stderr_stop_flag), daemon=True)
            ffmpeg_monitor_thread.start()

        except Exception as e:
            print(f"FFmpeg শুরু করতে ব্যর্থ: {e}", flush=True)
            ffmpeg_process = None
    finally:
         ffmpeg_restart_lock.release() # লক রিলিজ করুন


# --- FFmpeg স্ট্রিম বন্ধ করা ---
def stop_ffmpeg_stream(graceful_timeout=5):
    """চলমান FFmpeg প্রসেস বন্ধ করে"""
    global ffmpeg_process
    if ffmpeg_process:
        pid = ffmpeg_process.pid
        print(f"FFmpeg প্রসেস বন্ধ করা হচ্ছে (PID: {pid})...", flush=True)
        try:
            # প্রথমে SIGTERM পাঠান
            ffmpeg_process.terminate()
            ffmpeg_process.wait(timeout=graceful_timeout)
            print(f"FFmpeg প্রসেস (PID: {pid}) সফলভাবে বন্ধ হয়েছে (terminate)।", flush=True)
        except subprocess.TimeoutExpired:
            print(f"FFmpeg প্রসেস (PID: {pid}) terminate হয়নি, SIGKILL পাঠানো হচ্ছে...", flush=True)
            ffmpeg_process.kill()
            ffmpeg_process.wait()
            print(f"FFmpeg প্রসেস (PID: {pid}) সফলভাবে বন্ধ হয়েছে (kill)।", flush=True)
        except Exception as e:
            # Process might have already exited
            print(f"FFmpeg (PID: {pid}) বন্ধ করার সময় ত্রুটি বা এটি আগে থেকেই বন্ধ ছিল: {e}", flush=True)
        finally:
            ffmpeg_process = None # Ensure it's None


# --- FFmpeg প্রসেস ম্যানেজমেন্ট থ্রেড ---
def manage_ffmpeg_process():
    """FFmpeg প্রসেস মনিটর করে এবং এরর দিলে রিস্টার্ট করে (সমস্যাযুক্ত ফাইল বাদ দিয়ে)"""
    global ffmpeg_process, skipped_videos
    print("FFmpeg ম্যানেজমেন্ট থ্রেড চালু হয়েছে।", flush=True)

    while not stop_event.is_set():
        process_to_check = ffmpeg_process # Check the current global process
        if process_to_check:
            return_code = process_to_check.poll()

            if return_code is not None: # প্রসেস শেষ হয়ে গেছে
                # Ensure we don't act on a process that was intentionally stopped and cleared
                if process_to_check != ffmpeg_process and ffmpeg_process is not None:
                     # A new process might have started while we were polling the old one
                     print("একটি নতুন FFmpeg প্রসেস ইতিমধ্যে শুরু হয়েছে, পুরনোটির সমাপ্তি উপেক্ষা করা হচ্ছে।", flush=True)
                     time.sleep(5) # Prevent busy-looping
                     continue

                print(f"FFmpeg প্রসেস (PID: {process_to_check.pid}) কোড {return_code} দিয়ে শেষ হয়েছে।", flush=True)
                problem_file = None
                should_restart = True

                if return_code != 0: # এরর কোড
                    print("FFmpeg এরর দিয়ে শেষ হয়েছে। কারণ খোঁজা হচ্ছে...", flush=True)
                    # stderr থেকে সমস্যাযুক্ত ফাইল খোঁজার চেষ্টা
                    # এই প্যাটার্নটি আরও উন্নত করা দরকার হতে পারে
                    error_pattern = re.compile(r".*([\"']?(/[^/ '\" M]+)+/(video_\d+\.(?:mp4|mkv|avi))[\"']?).*(?:Error|Invalid data|Conversion failed|Cannot open)", re.IGNORECASE)
                    stderr_snapshot = list(ffmpeg_stderr_lines)
                    # print(f"Stderr স্ন্যাপশট ({len(stderr_snapshot)} লাইন): {stderr_snapshot}", flush=True)

                    for line in reversed(stderr_snapshot): # শেষ থেকে দেখুন
                        match = error_pattern.search(line)
                        if match and match.group(1):
                            try:
                                found_path = match.group(1).strip("'\"")
                                abs_found_path = os.path.abspath(found_path)

                                # চেক করুন এটি আমাদের ডাউনলোড করা ভিডিওগুলোর মধ্যে একটি কিনা
                                for video_path in downloaded_videos:
                                    if os.path.abspath(video_path) == abs_found_path:
                                        problem_file = video_path
                                        break # ফাইল পাওয়া গেছে
                                if problem_file:
                                    break # ভেতরের লুপ থেকেও বের হন
                            except Exception as e:
                                print(f"এরর লাইন পার্সিং এ সমস্যা: {e}", flush=True)


                    if problem_file:
                        abs_problem_file = os.path.abspath(problem_file)
                        if abs_problem_file not in skipped_videos:
                             print(f"সম্ভাব্য সমস্যাযুক্ত ফাইল সনাক্ত: {problem_file}। বাদ দেওয়ার তালিকায় যোগ করা হচ্ছে।", flush=True)
                             skipped_videos.add(abs_problem_file)
                             save_skipped_videos() # ফাইল সেভ করুন
                        else:
                             print(f"ফাইল {problem_file} আগে থেকেই বাদ দেওয়া তালিকায় ছিল।", flush=True)
                    else:
                        print("stderr থেকে নির্দিষ্ট সমস্যাযুক্ত ফাইল সনাক্ত করা যায়নি।", flush=True)

                    # যদি প্লেলিস্ট খালি হয়ে যায় বাদ দেওয়ার পর, তাহলে রিস্টার্ট করার চেষ্টা বন্ধ করুন
                    active_video_exists = any(os.path.abspath(v) not in skipped_videos for v in downloaded_videos)
                    if not active_video_exists:
                         print("কোনো সক্রিয় ভিডিও অবশিষ্ট নেই। FFmpeg রিস্টার্ট করা হবে না।", flush=True)
                         should_restart = False

                else:
                    # কোড 0 মানে স্বাভাবিকভাবে শেষ হয়েছে (যা আমাদের লুপে অপ্রত্যাশিত)
                    print("FFmpeg স্বাভাবিকভাবে শেষ হয়েছে (অপ্রত্যাশিত)। রিস্টার্ট করা হচ্ছে...", flush=True)

                # এখানে ffmpeg_process কে None সেট করা গুরুত্বপূর্ণ যাতে start_ffmpeg_stream আবার শুরু করতে পারে
                ffmpeg_process = None
                # stderr মনিটর থ্রেড স্বাভাবিকভাবেই শেষ হওয়ার কথা যখন প্রসেস শেষ হয়

                if should_restart and not stop_event.is_set():
                    print("FFmpeg রিস্টার্ট করার চেষ্টা করা হচ্ছে...", flush=True)
                    # রিস্টার্ট করার আগে একটু অপেক্ষা করা ভালো হতে পারে
                    time.sleep(2)
                    start_ffmpeg_stream(is_restart=True)
                elif not should_restart:
                     print("রিস্টার্ট করার দরকার নেই বা সম্ভব নয়।", flush=True)

            else:
                # প্রসেস এখনও চলছে, কিছুক্ষণ পর আবার চেক করুন
                pass # নিচে sleep আছে

        else:
            # FFmpeg প্রসেস চলছে না
            # যদি ডাউনলোড হওয়া এবং বাদ না দেওয়া ভিডিও থাকে, তাহলে শুরু করার চেষ্টা করুন
            active_video_exists = any(os.path.abspath(v) not in skipped_videos for v in downloaded_videos)
            if active_video_exists and not stop_event.is_set():
                print("FFmpeg চলছে না কিন্তু সক্রিয় ভিডিও আছে। শুরু করার চেষ্টা করা হচ্ছে...", flush=True)
                start_ffmpeg_stream(is_restart=False) # is_restart=False কারণ এটি নতুন শুরু
            elif not active_video_exists and downloaded_videos:
                 print("FFmpeg চলছে না এবং কোনো সক্রিয় ভিডিও নেই (সবগুলো বাদ দেওয়া হয়েছে?)", flush=True)


        # চেক করার মধ্যে একটি নির্দিষ্ট সময় বিরতি দিন
        time.sleep(5) # প্রতি ৫ সেকেন্ডে চেক করুন

    print("FFmpeg ম্যানেজমেন্ট থ্রেড বন্ধ হচ্ছে।", flush=True)


# --- ভিডিও ডাউনলোড ফাংশন (আগের মতই, শুধু অ্যাবসলিউট পাথ ব্যবহার নিশ্চিত করুন) ---
def download_video(url, index):
    global downloaded_videos
    try:
        filename = f"video_{index + 1}.mp4"
        filepath = os.path.join(VIDEO_DIR, filename)
        abs_filepath = os.path.abspath(filepath) # অ্যাবসলিউট পাথ

        # আগে থেকেই ডাউনলোড করা আছে কিনা চেক করুন (অ্যাবসলিউট পাথ দিয়ে)
        # This check might be redundant if we populate downloaded_videos carefully at start
        is_already_downloaded = any(os.path.abspath(v) == abs_filepath for v in downloaded_videos)

        if os.path.exists(filepath) and not is_already_downloaded:
            print(f"'{filename}' আগে থেকেই আছে কিন্তু লিস্টে নেই, যোগ করা হচ্ছে।", flush=True)
            if abs_filepath not in skipped_videos: # যদি বাদ দেওয়া না থাকে
                downloaded_videos.append(abs_filepath)
                downloaded_videos.sort() # வரிசை ঠিক রাখা
            return True # যেহেতু ফাইল আছে, ডাউনলোড সফল ধরা যায়

        if is_already_downloaded:
            # print(f"'{filename}' আগে থেকেই ডাউনলোড করা এবং লিস্টে আছে।")
            return True # ডাউনলোড সফল ধরা যায়

        if abs_filepath in skipped_videos:
            print(f"'{filename}' বাদ দেওয়া তালিকায় আছে, ডাউনলোড করা হচ্ছে না।", flush=True)
            return False # ডাউনলোড সফল নয় কারণ এটি বাদ দেওয়া

        # ডাউনলোড প্রক্রিয়া
        print(f"ডাউনলোড শুরু হচ্ছে: {url} -> {filepath}", flush=True)
        response = requests.get(url, stream=True, timeout=30) # টাইমআউট যোগ করা ভালো
        response.raise_for_status()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"সফলভাবে ডাউনলোড হয়েছে: {filename}", flush=True)
        if abs_filepath not in downloaded_videos:
            downloaded_videos.append(abs_filepath)
            downloaded_videos.sort()
        return True

    except requests.exceptions.RequestException as e:
        print(f"ভিডিও ডাউনলোড ব্যর্থ ({url}): {e}", flush=True)
        return False
    except Exception as e:
        print(f"ভিডিও সংরক্ষণ বা অন্য কোনো ত্রুটি ({url}): {e}", flush=True)
        return False

# --- ব্যাকগ্রাউন্ডে ভিডিও ডাউনলোড ---
def background_downloader():
    """ব্যাকগ্রাউন্ড থ্রেডে ভিডিও ডাউনলোড করে এবং প্রয়োজন হলে FFmpeg রিস্টার্ট ট্রিগার করে"""
    print("ব্যাকগ্রাউন্ড ডাউনলোডার থ্রেড চালু হয়েছে।", flush=True)
    initial_stream_started = False

    # শুরুতে ডিস্কে থাকা ভিডিওগুলো লিস্টে যোগ করুন
    for i in range(len(VIDEO_URLS)):
         filename = f"video_{i + 1}.mp4"
         filepath = os.path.join(VIDEO_DIR, filename)
         abs_filepath = os.path.abspath(filepath)
         if os.path.exists(filepath) and abs_filepath not in skipped_videos:
             if abs_filepath not in downloaded_videos:
                  downloaded_videos.append(abs_filepath)
                  downloaded_videos.sort()
                  print(f"ডিস্কে থাকা ভিডিও '{filename}' যোগ করা হয়েছে।", flush=True)

    while not stop_event.is_set():
        new_video_added = False
        all_videos_processed = True # Assume all are processed initially for this loop

        for i, url in enumerate(VIDEO_URLS):
            if stop_event.is_set(): break

            filepath = os.path.join(VIDEO_DIR, f"video_{i + 1}.mp4")
            abs_filepath = os.path.abspath(filepath)

            # যদি ডাউনলোড না হয়ে থাকে এবং বাদ দেওয়া না থাকে
            is_in_downloaded = any(os.path.abspath(v) == abs_filepath for v in downloaded_videos)
            if not is_in_downloaded and abs_filepath not in skipped_videos:
                all_videos_processed = False # Still videos left to attempt download
                print(f"ভিডিও {i+1} ডাউনলোড করার চেষ্টা করা হচ্ছে...", flush=True)
                if download_video(url, i):
                    print(f"নতুন ভিডিও '{os.path.basename(filepath)}' যোগ হয়েছে। FFmpeg রিস্টার্ট হতে পারে যদি প্রয়োজন হয়।", flush=True)
                    new_video_added = True
                    # FFmpeg রিস্টার্ট করার দায়িত্ব এখন manage_ffmpeg_process থ্রেডের
                    # তবে আমরা এখানে প্লেলিস্ট আপডেটের জন্য একটি ইঙ্গিত দিতে পারি
                    # create_ffmpeg_playlist() # প্লেলিস্ট আপডেট করুন (যদি FFmpeg রিস্টার্ট না করে)
                else:
                    # ডাউনলোড ব্যর্থ হলে কিছুক্ষণ অপেক্ষা করে আবার চেষ্টা করা যেতে পারে
                    print(f"ভিডিও {i+1} ডাউনলোড ব্যর্থ। পরের বার আবার চেষ্টা করা হবে।", flush=True)
                    # এই URL টিকে সাময়িকভাবে এড়িয়ে যাওয়া যেতে পারে বা ব্যর্থতার কাউন্টার রাখা যেতে পারে

        # যদি এই চক্রে নতুন কোনো ভিডিও সফলভাবে যোগ না হয় এবং সব ভিডিও প্রসেস করা হয়ে থাকে
        if not new_video_added and all_videos_processed:
            print("সকল ভিডিও ডাউনলোড বা স্কিপ করা সম্পন্ন। ডাউনলোডার থ্রেড নিষ্ক্রিয় হচ্ছে।", flush=True)
            break # লুপ থেকে বের হয়ে যান

        # পরের চেকের আগে কিছুক্ষণ অপেক্ষা করুন
        time.sleep(60) # প্রতি ১ মিনিট পর চেক করুন

    print("ব্যাকগ্রাউন্ড ডাউনলোডার থ্রেড শেষ হয়েছে।", flush=True)


# --- Flask Routes (আগের মতই) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream/<path:filename>')
def stream(filename):
    stream_path = os.path.abspath(STREAM_OUTPUT_DIR)
    try:
        # Security check (Path Traversal)
        requested_path = os.path.abspath(os.path.join(stream_path, filename))
        if not requested_path.startswith(stream_path):
             abort(404)
        # print(f"Serving file: {requested_path}", flush=True) # ডিবাগিং
        return send_from_directory(stream_path, filename, conditional=True) # conditional=True helps with caching
    except FileNotFoundError:
        # print(f"File not found: {requested_path}", flush=True) # ডিবাগিং
        abort(404)
    except Exception as e:
         print(f"Error serving file {filename}: {e}", flush=True)
         abort(500)


# --- অ্যাপ্লিকেশন বন্ধ করার হ্যান্ডলার ---
def signal_handler(sig, frame):
    print("\nবন্ধ করার সিগন্যাল পাওয়া গেছে...", flush=True)
    stop_event.set() # সব থ্রেডকে বন্ধ করার সিগন্যাল দিন
    # মনিটর থ্রেড এবং ডাউনলোডার থ্রেড stop_event দেখে বন্ধ হবে
    # FFmpeg প্রসেস বন্ধ করুন
    stop_ffmpeg_stream()
    print("অ্যাপ্লিকেশন বন্ধ হচ্ছে।", flush=True)
    exit(0)


# --- প্রধান চালক ---
if __name__ == '__main__':
    print("অ্যাপ্লিকেশন চালু হচ্ছে...", flush=True)
    load_skipped_videos() # শুরুতে বাদ দেওয়া ভিডিওর তালিকা লোড করুন

    # সিগন্যাল হ্যান্ডলার সেট করুন
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # ব্যাকগ্রাউন্ড ডাউনলোডার থ্রেড শুরু করুন
    downloader_thread = threading.Thread(target=background_downloader, daemon=True)
    downloader_thread.start()

    # FFmpeg ম্যানেজমেন্ট থ্রেড শুরু করুন
    ffmpeg_manager = threading.Thread(target=manage_ffmpeg_process, daemon=True)
    ffmpeg_manager.start()

    # Flask অ্যাপ চালু করুন (Gunicorn ব্যবহার করা উচিত প্রোডাকশনে)
    print("Flask অ্যাপ চালু হচ্ছে http://0.0.0.0:5000 এ...", flush=True)
    # প্রোডাকশনের জন্য: gunicorn -w 4 -b 0.0.0.0:5000 app:app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), threaded=True) # threaded=True ব্যবহার করা যেতে পারে, তবে gunicorn ভালো

    # অ্যাপ বন্ধ হওয়ার সময় নিশ্চিত করুন যে সব বন্ধ হয়েছে
    print("প্রধান থ্রেড শেষ হয়েছে।", flush=True)
    stop_event.set()
    # থ্রেডগুলো জয়েন করার জন্য অপেক্ষা করা যেতে পারে (যদি daemon=False হয়)
    stop_ffmpeg_stream()
