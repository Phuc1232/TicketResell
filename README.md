# TicketResell

# I . Giới thiệu
# 1.1 Mục đích

Mục đích tài liệu này là cung cấp một cái nhìn tổng quan dễ hiểu và thành phần dự án.

Xây dựng một nền tảng số cho phép người dùng đăng bán, tìm kiếm và mua lại các vé sự kiện (bao gồm các buổi sự kiện giải trí - nghệ thuật, sự kiện thể thao, sự kiện giáo dục và sự kiện thương mại - tiêu dùng) chưa sử dụng một cách an toàn, tiện lợi và minh bạch.

Tài liệu được làm ra để cho sinh viên trực tiếp tham gia phát triển dự án để phục vụ cho việc hoàn thành đồ án. Ngoài ra trong môi trường thực tế bên ngoài tài liệu này phục vụ cho nhà phát triển website, kiểm thử viên, nhà quản lý dự án và các sinh viên để tham khảo.

# 1.2 Phạm vi

Tài liệu đặc tả yêu cầu phần mềm này được xây dựng nhằm phục vụ cho dự án Xây dựng nền tảng bán lại vé sự kiện chưa sử dụng.

Việc xây dựng nền tảng bán lại vé chưa sử dụng sẽ giúp giải quyết nhiều vấn đề mua bán của người tiêu dùng và mang lại nhiều tiện ích:

Giải quyết vấn đề tổn thất tài chính khi vé tham gia sự kiện được bán ra nhưng không sử dụng dẫn đến lãng phí cho người mua và thiệt thòi cho người cần mua vé.

Người mua lại vé sự kiện cần tìm một nền tảng trao đổi đáng tin cậy và thao tác tiện lợi khi giao dịch.

Ngoài ra nền tảng còn cung cấp đầy đủ thông tin cần thiết về sự kiện mà người mua cần tìm kiếm. 

# 1.3 Thuật ngữ và từ viết tắt, định nghĩa 

| Thuật ngữ | Định nghĩa |
|---|---|
| 1. Software Requirements Specifications (SRS)| Đặc tả yêu cầu phầm mềm | 
| 2. Use Case | Các trường hợp sử dụng |
| 3. Websites | Trang mạng |
| 4. Menu | Danh sách |
| 5. Hypertext Transfer Protocol - HTTPS | Giao thức truyền tải siêu văn bản |
| 6. Entity Relationship Diagram | Mô hình thực thể kết hợp |
| 7. Web server | Phần mềm máy chủ cung cấp các chức năng tài nguyên cho máy khách |
| 8. Python, Flask Api, React | Ngôn ngữ lập trình |
# 1.4 Tài liệu tham khảo

 

# 1.5 Tổng quan 

Với cấu trúc này ta có 3 phần : 

Phần 1 : Cung cấp cái nhìn tổng quan về thành phần của SRS

Phần 2: Mô tả tổng quan các nhân tố , đặc điểm người dùng ,môi trường được thực hiện tác động lên hệ thống và nhu cầu của nó 

Phần 3 : Các yêu cầu phi chức năng 
# II. Yêu cầu chức năng 
# 2.1 Các tác nhân 
Hệ thống nền tảng gồm có các tác nhân là Khách, Quản trị viên, Thành viên, Cổng thanh toán. Trong đó:

- Khách: Là người dùng chưa có tài khoản trên hệ thống. Vai trò chính của họ là trải nghiệm các tính năng cơ bản của website như xem thông tin vé hoặc giới thiệu về nề tảng mà không cần phải đăng nhập và đăng ký.

- Quản trị viên: Có vai trò là quản lý hoạt động của hệ thống website. Họ có quyền truy cập các tính năng quản lý như quản lý thành viên, quản lý vé sự kiện, xác nhận giao dịch, hỗ trợ giải đáp thắc mắc đối với người dùng và xem các báo cáo về hoạt động hệ thống.

- Thành viên: Là những tài khoản đã đăng ký và đăng nhập vào hệ thống. Những tài khoản này có chức năng tìm kiếm vé sự kiện mà mình muốn mua hoặc đăng bán vé, trao đổi với bên chủ hoặc khách hàng mua vé.

- Cổng thanh toán: Là dịch vụ trung gian giúp kết nối giữa người mua, người bán và bên ngân hàng. Hệ thống sẽ gửi yêu cầu thanh toán đến cổng, cổng sẽ có nhiệm vụ xác minh thanh toán và trả lại trạng thái thanh toán (thành công/thất bại).

<img width="1061" height="673" alt="image" src="https://github.com/user-attachments/assets/c7750559-b922-492f-aead-3c83d438c345" />

<p align="center">
 Hình 1-Sơ đồ bối cảnh
</p>

# 2.2 Các chức năng của hệ thống:

Nền tảng bán lại vé có các chức năng sau:

a. Chức năng dành cho Khách:

- Tìm kiếm vé của sự kiện cần mua.

- Xem thông tin sự kiện, loại vé của sự kiện đó.

- Đăng nhập/Đăng ký.

b, Chức năng dành cho Quản trị viên:

- Quản lý hệ thống nền tảng và hệ thống thành viên (người dùng đã đăng ký tài khoản).

- Phê duyệt các giao dịch, giải quyết các vấn đề tranh chấp, hoàn lại tiền.

- Xem nhật ký hoạt động (giao dịch, phê duyệt, khiếu nại).

- Thống kê và báo cáo doanh thu, người dùng.

c. Chức năng dành cho Thành viên:

- Tìm kiếm và mua vé sự kiện mà mình mong muốn.

- Bán lại vé chưa được sử dụng.

- Cập nhật thông tin cá nhân.

- Đổi password

- Đăng bài viết (tìm hoặc bán vé), bình luận, đánh giá.

- Chat trực tiếp với người mua/bán.

- Nhận thông báo về sự kiện, giao dịch, thanh toán.

d. Chức năng cho Cổng thanh toán:

- Gửi yêu cầu thanh toán khi thành viên xác nhận mua vé.

- Kiểm tra trạng thái giao dịch.

- Thông báo kết quả thanh toán cho bên hệ thống. 

# 2.3 Biểu đồ use case tổng quan
<img width="787" height="723" alt="image" src="https://github.com/user-attachments/assets/e0ff6402-9589-4ead-8343-21a3b52b2673" />
<p align="center">
Hình 2- Biểu đồ  use case tổng quan 
</p>
  
# 2.4 Luồng xử lý
<img width="1182" height="607" alt="image" src="https://github.com/user-attachments/assets/3d217957-a28c-4718-9c3b-7e33f7a7eec8" />
<p align="center">
Hình 4 -Biểu đồ luồng xử lý
</p>
  
# 2.5 Luồng xử lý chi tiết

# 2.5.1 Luồng xử lý đăng ký
<img width="954" height="624" alt="image" src="https://github.com/user-attachments/assets/ee215097-ab0b-450a-b742-38e5ed188d8e" />
<p align="center">
Hình 5 - Biểu đồ đăng ký 
</p>
  
# 2.5.2 Luồng xử lý mua vé
<img width="1068" height="789" alt="image" src="https://github.com/user-attachments/assets/54260047-f8ea-4728-b987-a36311a9acf4" />
<p align="center">
Hình 6 - Biểu đồ mua vé 
</p>
  
# 2.5.3 Luồng xử lý bán vé 
<img width="1190" height="774" alt="image" src="https://github.com/user-attachments/assets/738f0487-fa91-40a2-8c5b-6d38b3bd6ab7" />
<p aligb="center">
Hình 7 - Biểu đồ bán vé 
</p> 

# 2.5.4 Luồng xử quản lý vé
<img width="1015" height="722" alt="image" src="https://github.com/user-attachments/assets/e330f2ad-a73e-4c58-9372-ba1cfa082ac8" />
<p align="center">
Hình 8 - Biểu đồ quản lý vé 
</p>

# 2.6 Thiết kế cơ sỡ dữ liệu

# 2.6.1 Mô hình ERD
<img width="1527" height="759" alt="image" src="https://github.com/user-attachments/assets/93bd9d25-6755-47e8-8194-14d29d659306" />
<p align="center">
Hình 9 - Biểu đồ ERD
</p>

# 2.6.2 Mô hình cơ sở dữ liệu 
<img width="1186" height="739" alt="image" src="https://github.com/user-attachments/assets/6027aeb3-3ec9-4ea8-a13b-f587ec64311d" />
<p align="center">
Hình 10 - Biểu đồ cơ sở dữ liệu
</p>

# III.Yêu cầu phi chức năng




