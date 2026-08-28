# Frontend Coding Rules

## Rule 0: Tuân thủ cấu trúc thư mục & Vai trò Folder

- Bắt buộc phải đặt mã nguồn vào đúng thư mục tương ứng với vai trò của nó dưới đây. Không tự ý tạo thư mục root mới hoặc đặt sai vị trí quy định.

| Thư mục            | Mục tiêu / Mô tả                                                                                                                                                                                |
| :----------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/app/`         | Next.js App Router (chứa nhóm routing bảo mật `app/` sau đăng nhập và route công khai `(public)/`).                                                                                             |
| `src/app/actions/` | Chứa các Next.js Server Actions dùng để tương tác trực tiếp với API phía Backend một cách an toàn.                                                                                              |
| `src/components/`  | Chứa các React components tái sử dụng trong dự án (Header, Sidebar, Table, UI components chung).                                                                                                |
| `src/config/`      | Lưu trữ cấu hình ứng dụng (endpoints, route paths) và cấu hình giao diện UI.                                                                                                                    |
| `src/contexts/`    | Định nghĩa các React Context Provider để chia sẻ state toàn cục (ví dụ: Sidebar State, Theme).                                                                                                  |
| `src/hooks/`       | Chứa các custom React Hooks xử lý logic độc lập (useDebounce, useTable, useMediaQuery).                                                                                                         |
| `src/stores/`      | Quản lý state tập trung cho client-side thông qua Zustand (Zustand Stores).                                                                                                                     |
| `src/styles/`      | Lưu trữ cấu hình CSS giao diện (màu sắc, font chữ, scrollbar, Tailwind custom). **Lưu ý:** Khi làm UI phải tuân thủ đúng các tông màu được cấu hình tại đây để đồng bộ màu nhận diện của dự án. |
| `src/types/`       | Định nghĩa TypeScript types/interfaces (cần đồng bộ khớp với Schema Backend).                                                                                                                   |
| `src/utils/`       | Các hàm tiện ích dùng chung (API client, format, toast, helpers).                                                                                                                               |

## Rule 1: Dùng `index.ts` để barrel-export

- Mỗi folder nhiều file (types, components, hooks, utils, stores, contexts, config...) phải có `index.ts` để re-export.
- Chỉ import từ folder-level (ví dụ: `import type { ExportBatch, Label } from '@/types'`), không import trực tiếp file con.

## Rule 2: Đặt Type tập trung tại `src/types/`

- Mọi TS type/interface nghiệp vụ (API response, DTO, entity, enum...) phải đặt trong `src/types/`, không viết inline trong component/page hay export ngược từ component.

## Rule 3: Sử dụng component có sẵn

- Trước khi tạo component mới, phải check `src/components/`. Dùng lại hoặc extend component đã có, tuyệt đối không tạo trùng lặp.
- **Bắt buộc:** Phải hỏi lại người dùng xem component đó đã có hoặc đã được phát triển ở nhánh/thư mục khác chưa trước khi tiến hành tạo mới.

## Rule 4: Data Fetching ở cấp độ Page (Server-side)

- Ưu tiên gọi API để lấy dữ liệu từ Backend trực tiếp ở phía Server (Server Components / Page level).
- Sau khi lấy được dữ liệu, thực hiện truyền (pass down) dữ liệu đó làm props cho các component con hoặc UI components hiển thị ở phía Client.

## Rule 5: Chia nhỏ Component để tối ưu hóa khả năng bảo trì (Maintainability)

- Không viết code quá dài trong một file Page hoặc Component duy nhất.
- Bắt buộc phải phân tách Page lớn thành các sub-components nhỏ hơn có vai trò độc lập, giúp code gọn gàng, dễ kiểm thử và dễ bảo trì.
- **Tái sử dụng:** Nếu nhận thấy một component con có khả năng hoặc đang được tái sử dụng ở nhiều nơi khác nhau, hãy ưu tiên tách nó ra thư mục `src/components/` chung của toàn app.

## Rule 6: Quy tắc đặt tên file & Component (Naming Conventions)

- **Tên file:** Sử dụng định dạng gạch ngang (`kebab-case`). Đặt tên ưu tiên tính ngữ nghĩa, mô tả rõ chức năng của file để dễ hiểu mục đích sử dụng (ví dụ: `header-wrapper.tsx`, `header-avatar.tsx`).
- **Tên Component:** Khai báo bằng chữ hoa đầu từ (`PascalCase`) bình thường bên trong mã nguồn (ví dụ: component trong file `header-wrapper.tsx` vẫn export `HeaderWrapper`).

## Rule 7: Quy chuẩn định dạng mã nguồn (Code Formatting)

- Khi làm UI hoặc phát triển frontend, ưu tiên format code theo cấu hình dưới đây:

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100
}
```

## Rule 8: Chú thích cho các hàm và logic tính toán (Logic Comments)

- Khi viết các hàm (functions) hoặc các đoạn xử lý tính toán logic, bắt buộc phải có ít nhất **1 dòng comment ngắn gọn** mô tả rõ mục đích/logic của hàm hoặc khối xử lý đó.

## Rule 9: Bắt buộc viết tài liệu hướng dẫn cho Component (Component Documentation)

- Khi viết hoặc tạo mới các reusable components (đặc biệt trong thư mục `src/components/`), bắt buộc phải tạo kèm một file `docs.md` ngay bên trong thư mục của component đó.
- Cấu trúc file `docs.md` phải đầy đủ các phần tương tự như ví dụ tại `src/components/table/docs.md`:
  1. **Hướng dẫn sử dụng nhanh (Quick Start/Steps):** Cách tích hợp vào page, code mẫu Server và Client component.
  2. **Các tham số cấu hình (Props API):** Bảng mô tả chi tiết tên prop, kiểu dữ liệu, bắt buộc hay không, và chức năng.
  3. **Chi tiết cấu hình nâng cao:** Giải thích chi tiết các object configuration hoặc các types đi kèm.
  4. **Ví dụ code mẫu cụ thể.**

## Rule 10: Cấu hình UI tập trung (Unified UI Configuration)

- Khi phát triển giao diện UI, nếu cần các cấu hình đồng nhất (như kích thước header, sidebar, màu nền mặc định, chiều cao các section...), bắt buộc phải khai báo và quản lý tập trung tại `src/config/ui.ts`. Không khai báo rải rác các giá trị hardcode trong từng component riêng lẻ.

## Rule 11: Cấu hình ứng dụng tập trung (App Configuration)

- Mọi cấu hình chung liên quan đến ứng dụng (như tên ứng dụng `APP_NAME`, phiên bản `APP_VERSION`, các API endpoints mặc định, Media base URL...) phải được khai báo và quản lý tập trung tại `src/config/app.ts`.
- **Bắt buộc:** Tất cả mã nguồn trong dự án khi cần sử dụng cấu hình hoặc biến môi trường phải import thông qua `src/config/app.ts`. Tuyệt đối không gọi trực tiếp các biến môi trường (như `process.env.NEXT_PUBLIC_...`) bên trong các components hoặc pages riêng lẻ.
