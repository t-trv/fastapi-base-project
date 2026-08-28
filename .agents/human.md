# Hướng dẫn tạo cây cấu trúc dự án (Project Structure)

Để xuất cấu trúc dự án ra file `tree.txt` phục vụ cho việc đọc hiểu source code của Agent, thực hiện các bước sau:

### 1. Cài đặt công cụ `tree`

```bash
sudo apt update && sudo apt install tree -y
```

### 2. Xuất cây cấu trúc dự án (bỏ qua các thư mục build/cache)

Chạy lệnh sau tại thư mục gốc của dự án:

```bash
tree -I "node_modules|.next|__pycache__|.venv|env|dist|build|.git|.pytest_cache" -L 4 > .agents/structure.md
```
