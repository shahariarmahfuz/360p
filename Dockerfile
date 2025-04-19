# বেস ইমেজ হিসাবে একটি Python 3.9 slim সংস্করণ ব্যবহার করুন
FROM python:3.9-slim

# সিস্টেম প্যাকেজ আপডেট করুন এবং ffmpeg ইনস্টল করুন
# wget এবং ca-certificates যোগ করা হল https ডাউনলোড এর জন্য (যদি প্রয়োজন হয়)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    wget \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ওয়ার্কিং ডিরেক্টরি সেট করুন
WORKDIR /app

# প্রয়োজনীয় Python লাইব্রেরি ইনস্টল করার জন্য requirements.txt কপি করুন
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# অ্যাপ্লিকেশনের সোর্স কোড কপি করুন
COPY app.py .
# যদি টেমপ্লেট ফোল্ডার ব্যবহার করেন তবে সেটাও কপি করুন (এই উদাহরণে নেই)
# COPY templates/ templates/

# ভিডিও এবং HLS ফাইল রাখার জন্য ভলিউম তৈরি করুন (ঐচ্ছিক, তবে ডেটা ধরে রাখার জন্য ভাল)
# এই ডিরেক্টরিগুলো অ্যাপ কোডের মাধ্যমেও তৈরি হবে, তবে Dockerfile এ উল্লেখ করা ভাল অভ্যাস
RUN mkdir -p /app/videos && mkdir -p /app/hls
# VOLUME /app/videos
# VOLUME /app/hls

# Flask অ্যাপের জন্য পোর্ট এক্সপোজ করুন (ডিফল্ট 5000)
EXPOSE 5000

# কন্টেইনার চালু হলে Flask অ্যাপটি রান করার কমান্ড
# CMD ["python", "app.py"]
# অথবা gunicorn ব্যবহার করতে পারেন আরও ভালো পারফরম্যান্সের জন্য
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
# যেহেতু FFmpeg একটি দীর্ঘস্থায়ী প্রসেস, একটি worker যথেষ্ট হতে পারে
CMD ["python", "app.py"]
