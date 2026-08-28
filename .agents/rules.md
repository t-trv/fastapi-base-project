# Coding Rules

## Rule base

- Không tự ý sửa/xóa rule cũ trừ khi được yêu cầu rõ ràng.
- Thêm rule mới thì đọc toàn bộ file và append vào cuối.
- Khi viết rule mới, phải viết ngắn gọn, súc tích và đi thẳng vào vấn đề (tương tự format hiện tại).
- Không tự ý refactor hay đổi số thứ tự các rule cũ. Rule 0 là bất khả xâm phạm.

# Source Structure Rules

- Khi cần hiểu cấu trúc dự án hoặc tìm vị trí file, HÃY ĐỌC file `STRUCTURE.md` ở thư mục gốc trước.
- Không tự động chạy lệnh liệt kê tất cả các file (`ls -R` hoặc quét toàn bộ folder) trừ khi được yêu cầu đích danh.

# Task Context Rules

- Nếu thực hiện các tác vụ liên quan đến Frontend, bắt buộc phải đọc và tuân thủ các quy tắc trong [frontend.md](frontend.md).
- Nếu thực hiện các tác vụ liên quan đến Backend, bắt buộc phải đọc và tuân thủ các quy tắc trong [backend.md](backend.md).

# AG RULES: CONCISE & PUNCHY RESPONSES

## 1. Response Style & Tone (Bắt buộc)

- **Cực kỳ ngắn gọn & trực diện:** Đi thẳng vào câu trả lời hoặc giải pháp. KHÔNG chào hỏi, KHÔNG cảm ơn, KHÔNG tóm tắt lại câu hỏi của người dùng.
- **Không giải thích thừa:** Chỉ giải thích code khi thực sự cần thiết (tối đa 1-2 câu). Bỏ qua các câu dẫn dắt kiểu "Dưới đây là...", "Hy vọng giúp ích...", "Chúc bạn thành công...".
- **Định dạng scannable:** Ưu tiên dùng Bullet points và Bold từ khóa chính. Không viết văn xuôi dài dòng.

## 2. Code Generation Rules

- **Chỉ trả về Diff / Code sửa đổi:** Không in lại toàn bộ file code nếu chỉ sửa vài dòng. Chỉ đưa đoạn code cần thay đổi kèm context đủ để biết chèn vào đâu.
- **Strict Typing:**
  - Backend (Python/FastAPI): Dùng Pydantic v2, Type Hints bắt buộc cho mọi function.
  - Frontend (Next.js/TypeScript): Dùng TypeScript strict mode, tuyệt đối không dùng `any`.
- **Clean Architecture:**
  - Frontend: Ưu tiên React Server Components (Next.js App Router). Chỉ thêm `'use client'` khi bắt buộc.
  - Backend: Dùng async/await cho FastAPI routes và DB operations.
- **Clean Code & Comments:**
  - Code comment phải viết bằng tiếng Việt, viết hoa chữ cái đầu tiên, ngắn gọn và chỉ viết khi thực sự cần thiết.
  - Tuân thủ nguyên tắc DRY (Don't Repeat Yourself), viết code sạch, tối ưu và dễ đọc.

## 3. Token & Context Optimization

- **Source Tree:** Ưu tiên đọc file `STRUCTURE.md` hoặc `tree.txt` ở root để hiểu cấu trúc dự án. KHÔNG tự động chạy lệnh quét/list toàn bộ file.
- **Terminal & Logs:** Khi chạy terminal gặp lỗi (ví dụ: `pytest` hoặc `npm run build`), CHỈ đọc và phân tích tối đa 10-15 dòng log lỗi cuối cùng.
- **File Exclusions:** Bỏ qua hoàn toàn các folder build, cache (`node_modules`, `.next`, `__pycache__`, `.venv`, `dist`, `.git`).

## 4. Default Communication

- Trả lời bằng tiếng Việt ngắn gọn.
- Nếu thông tin chưa đủ để viết code, chỉ hỏi lại ĐÚNG 1 câu làm rõ điểm thắc mắc, không đoán mò.
