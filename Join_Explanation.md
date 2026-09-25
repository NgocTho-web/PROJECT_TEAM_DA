# Báo cáo Tích hợp Dữ liệu (Data Integration) - M2
**Thực hiện bởi:** Phạm Văn Qui

## 1. Các phư

ơng pháp đã sử dụng
- **pd.concat():** Sử dụng để nối dọc (Vertical Integration) các bảng dữ liệu tĩnh (Static Data) có cùng cấu trúc với nhau để tạo thành một bảng `Unified Static Master Table` duy nhất.
- **pd.merge():** Sử dụng để nối ngang (Horizontal Integration) bảng Master Table vừa tạo với bảng dữ liệu động (`Dynamic Data`) dựa trên khóa chính là cột `customer_id` (hoặc CustomerID).

## 2. Giải thích lý do chọn loại Join
- **Loại Join đã chọn:** `Left Join` (how='left')
- **Lý do:** Bảng bên trái (Left) là danh sách khách hàng chuẩn (`Unified Static Master Table`). Việc dùng Left Join giúp giữ lại toàn bộ danh sách khách hàng gốc này. Bảng bên phải (Right) là dữ liệu động chứa các giao dịch/tương tác mới. Chúng ta chỉ đắp thêm thông tin động vào những khách hàng đã có sẵn trong danh sách gốc.
- **Dữ liệu thay đổi như thế nào sau khi Join:** 
  - Số lượng dòng (rows) của tập dữ liệu cuối cùng sẽ tối thiểu bằng với số dòng của bảng danh sách khách hàng ban đầu. 
  - Số lượng cột (columns) sẽ tăng lên do được cộng gộp các trường dữ liệu từ bảng động.
  - Những khách hàng có trong danh sách gốc nhưng chưa có dữ liệu giao dịch động sẽ có giá trị rỗng (`NaN` hoặc `Null`) ở các cột mới được thêm vào.