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
<p align="center">
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

# III. Yêu cầu phi chức năng

# 1. Hiệu suất 
- Thời gian tải trang & phản hồi API: không quá 3 giây thời gian phản hồi không quá 1 giây là hợp lý. Đặc biệt quan trọng trong các trang tìm kiếm sự kiện và chi tiết vé.

- Hỗ trợ đồng thời (Concurrency): ít nhất 30 người dùng là quá thấp. Một sự kiện có thể thu hút hàng nghìn hoặc chục nghìn người dùng đồng thời tại thời điểm mở bán hoặc ngay trước giờ diễn ra.

- Đề xuất: Hệ thống phải chịu tải được ít nhất 5,000 người dùng đồng thời trong các thời điểm cao điểm (flash sale, sự kiện lớn). Cần có cơ chế "hàng đợi"  ảo để tránh sập hệ thống.

- Tối ưu hóa: Rất quan trọng. Bổ sung:

- Cập nhật dữ liệu thời gian thực: Tình trạng vé (còn/hết), giá vé phải được cập nhật gần như ngay lập tức trên giao diện người dùng mà không cần tải lại trang để tránh trường hợp hai người cùng mua một vé.

- Sử dụng CDN (Content Delivery Network) để phân phối hình ảnh, CSS, JS nhanh hơn trên toàn cầu.

# 2. Bảo mật 
- Mã hóa dữ liệu nhạy cảm: Bắt buộc. Không chỉ là mật khẩu, mà còn là thông tin thanh toán, thông tin cá nhân (CCCD/Passport nếu có yêu cầu xác thực).

- Chống tấn công SQL Injection, XSS: Cơ bản và bắt buộc.

- Logging: Cần ghi log chi tiết các hoạt động:

- Giao dịch tài chính (mua, bán, rút tiền).

- Thay đổi thông tin vé (giá, số lượng).

- Đăng nhập, đăng xuất, các lần thử đăng nhập thất bại.

- Backup dữ liệu: Rất quan trọng.

- Bảo mật giao dịch: Tuân thủ tiêu chuẩn PCI DSS ( Payment Card Industry Data Security Standard) nếu trực tiếp xử lý thông tin thẻ tín dụng. Tích hợp với các cổng thanh toán uy tín (PayPal, Momo, VNPAY...) để giảm thiểu rủi ro.

- Chống gian lận:

  Hệ thống cần có cơ chế phát hiện các hành vi đáng ngờ 

  Xác thực người bánđể tăng độ tin cậy.

  Xác thực vé: Nếu có thể, tích hợp API với nhà tổ chức sự kiện để kiểm tra tính hợp lệ của mã vạch/QR code của vé.

# 3. Khả năng mở rộng
- Kiến trúc module hóa: Rất tốt. Ví dụ: module quản lý người dùng, module quản lý sự kiện, module thanh toán, module tìm kiếm.

- Khả năng tích hợp: Cần xác định rõ các hệ thống cần tích hợp:

- Bắt buộc: Cổng thanh toán, Dịch vụ email/SMS (để gửi thông báo, mã OTP).

- Nên có: Nền tảng mạng xã hội (để đăng nhập/chia sẻ), Google Maps (hiển thị địa điểm), Dịch vụ phân tích (Google Analytics).

- Documentation: Cần có API documentation rõ ràng cho cả việc bảo trì nội bộ và tích hợp bên ngoài trong tương lai.

# 4. Giao diện người dùng (UI/UX)
- Thiết kế responsive: Bắt buộc. Phần lớn người dùng sẽ truy cập qua di động.

- Thời gian học sử dụng: Không quá 30 phút  là một mục tiêu tốt. Quy trình mua vé và đăng bán vé phải cực kỳ đơn giản và trực quan.

- Luồng mua vé: Tìm kiếm -> Chọn vé -> Thanh toán -> Nhận vé. Chỉ nên có 3-4 bước.

- Luồng bán vé: Đăng nhập -> Điền thông tin vé -> Đặt giá -> Đăng bán.

- Giao diện nhất quán: Rất tốt.

- Bổ sung:

- Tìm kiếm và bộ lọc mạnh mẽ: Người dùng cần lọc sự kiện theo: Tên, địa điểm, ngày tháng, danh mục (nhạc, thể thao...), khoảng giá.

- Hiển thị thông tin vé rõ ràng: Sơ đồ chỗ ngồi nếu có, vị trí (khu, hàng, ghế), các lưu ý đặc biệt (vé có tầm nhìn hạn chế, vé điện tử/vé cứng).

# 5. Tương thích 
- Danh sách của bạn đã rất đầy đủ và chính xác. Tối ưu cho kết nối mạng chậm là một điểm cộng lớn, đặc biệt khi người dùng đang ở khu vực đông người, sóng yếu.

# 6. Độ tin cậy 
- Uptime tối thiểu 99.9%: Downtime vào thời điểm một sự kiện hot đang được giao dịch có thể gây thiệt hại tài chính và uy tín nặng nề.

- Thời gian phục hồi sau sự cố < 4 giờ

- Backup dữ liệu hàng ngày: Cần có cơ chế kiểm tra tính toàn vẹn của bản backup.

- Phương án dự phòng: Cần có hệ thống dự phòng , cân bằng tải để đảm bảo hệ thống luôn hoạt động ngay cả khi một máy chủ gặp sự cố.

# 7. Khả năng bảo trì 
- Đây là những tiêu chuẩn cho một dự án chuyên nghiệp.

- Code được viết theo chuẩn clean code

- Tài liệu kỹ thuật chi tiết

- Dễ dàng rollback khi cần thiết

# 8. Pháp lý và Tuân thủ 
- Tuân thủ quy định địa phương: Phải tuân thủ luật pháp của từng quốc gia/khu vực về việc bán lại vé (chống bán vé chợ đen với giá cắt cổ ). Một số nơi có thể giới hạn mức giá bán lại không được vượt quá một tỷ lệ % nhất định so với giá gốc.

- Chính sách và Điều khoản rõ ràng: Hệ thống phải có các trang chính sách (Terms of Service, Privacy Policy) dễ hiểu, quy định rõ:

- Phí dịch vụ của nền tảng (cho người mua và người bán).

- Quy trình giải quyết tranh chấp (khi vé là giả, sự kiện bị hủy/hoãn).

- Trách nhiệm của người bán và người mua.

# 9. Hỗ trợ và Vận hành
- Hỗ trợ khách hàng: Hệ thống phải có công cụ để đội ngũ hỗ trợ khách hàng có thể:

- Tra cứu thông tin giao dịch, thông tin người dùng.

- Tạm khóa giao dịch, tạm khóa tài khoản khi có tranh chấp.

- Hỗ trợ quá trình hoàn tiền (refund).

- Quản lý nội dung: Phải có giao diện quản trị để kiểm duyệt các sự kiện được đăng, quản lý người dùng, và xem báo cáo.






