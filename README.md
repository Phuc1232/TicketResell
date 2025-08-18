# 🎫 TicketResell – Nền tảng bán lại vé chưa sử dụng



# I. Giới thiệu
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
| 1.Software Requirements Specifications (SRS) | Đặc tả yêu cầu phần mềm|
| 2.Use Case(s) | các trường hợp sử dụng  |
| 3.Websites | Trang mạng |
| 4.Menu | Danh sách |
| 5.Hypertext Transfer Protocol - HTTPS | Giao thức truyền tải siêu văn bản |
| 6.Entity Relationship Diagram | Mô hình thực thể kết hợp |
| 7.Web server | Phần mềm máy chủ cung cấp các chức năng tài nguyên cho máy khách |
| 8.Python, Flask Api, React | Ngôn ngữ lập trình |

# 1.4 Tài liệu tham khảo
- [Ch14_Designing Object-Oriented Software Architectures.pptx](https://github.com/user-attachments/files/21828461/Ch14_Designing.Object-Oriented.Software.Architectures.pptx)
- [Ch15_Designing Client Server Software Architectures.pptx](https://github.com/user-attachments/files/21828463/Ch15_Designing.Client.Server.Software.Architectures.pptx)
- [Ch16_Designing Service-Oriented Architectures (1).pptx](https://github.com/user-attachments/files/21828465/Ch16_Designing.Service-Oriented.Architectures.1.pptx)
- [Ch17_Designing Component-Based Software Architectures.pptx](https://github.com/user-attachments/files/21828468/Ch17_Designing.Component-Based.Software.Architectures.pptx)

# 1.5 Tổng quan 

Với cấu trúc này ta có 3 phần : 

- Phần 1 : Cung cấp cái nhìn tổng quan về thành phần của SRS

- Phần 2: Mô tả tổng quan các nhân tố , đặc điểm người dùng ,môi trường được thực hiện tác động lên hệ thống và nhu cầu của nó 

- Phần 3 : Các yêu cầu phi chức năng 
# II. Yêu cầu chức năng
# 2.1 Các tác nhân

Hệ thống nền tảng gồm có các tác nhân là Khách, Quản trị viên, Thành viên, Cổng thanh toán. Trong đó:

- Khách: Là người dùng chưa có tài khoản trên hệ thống. Vai trò chính của họ là trải nghiệm các tính năng cơ bản của website như xem thông tin vé hoặc giới thiệu về nề tảng mà không cần phải đăng nhập và đăng ký.

- Quản trị viên: Có vai trò là quản lý hoạt động của hệ thống website. Họ có quyền truy cập các tính năng quản lý như quản lý thành viên, quản lý vé sự kiện, xác nhận giao dịch, hỗ trợ giải đáp thắc mắc đối với người dùng và xem các báo cáo về hoạt động hệ thống.

- Thành viên: Là những tài khoản đã đăng ký và đăng nhập vào hệ thống. Những tài khoản này có chức năng tìm kiếm vé sự kiện mà mình muốn mua hoặc đăng bán vé, trao đổi với bên chủ hoặc khách hàng mua vé.

- Cổng thanh toán: Là dịch vụ trung gian giúp kết nối giữa người mua, người bán và bên ngân hàng. Hệ thống sẽ gửi yêu cầu thanh toán đến cổng, cổng sẽ có nhiệm vụ xác minh thanh toán và trả lại trạng thái thanh toán (thành công/thất bại).
<img width="1061" height="673" alt="image" src="https://github.com/user-attachments/assets/b733679e-67a3-465b-9928-22784d46f686" />
<div align="center">
 Bảng 1: Sơ đồ bối  cảnh 
</div>

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

- Thông báo kết quả thanh toán cho bên hệ thống

# 2.3 Biểu đồ use case tổng quan
<img width="787" height="723" alt="image" src="https://github.com/user-attachments/assets/4023d3e4-ab81-45e5-8623-ded06d8bb99b" />
<div align="center">
 Bảng 2: Sơ đồ use case tổng quan
</div>

# 2.3.a. Sơ đồ Use case khách
<img width="637" height="545" alt="image" src="https://github.com/user-attachments/assets/4083a9a2-c880-40fd-8583-f3b35720bfc3" />
<div align="center">
 Bảng 2.a: Sơ đồ use case khách
</div>

# 2.3. b. Sơ đồ use case thành viên
<img width="849" height="735" alt="image" src="https://github.com/user-attachments/assets/58068fb3-4fb8-4ae3-ae69-c30b2d6508a4" />
<div align="center">
 Bảng 2.b : Sơ đồ use case thành viên
</div>

# 2.3.c Sơ đồ use case quản trị viên 
<img width="802" height="722" alt="image" src="https://github.com/user-attachments/assets/08667395-5b27-4273-b2b0-9e7c30747da4" />
<div align="center">
 Bảng 2.3.c : Sơ đồ use case quản trị viên
</div>

# 2.3.d Sơ đồ use case cổng thanh toán
<img width="780" height="700" alt="image" src="https://github.com/user-attachments/assets/3f7be334-c4e3-47eb-b28f-0b0ea91839e5" />
<div align="center">
 Bảng 2.3.d : Sơ đồ use case cổng thanh toán
</div>

# 2.5 Luồng xử lý chi tiết
# 2.5.1 Luồng xử lý đăng ký
<img width="954" height="624" alt="image" src="https://github.com/user-attachments/assets/7f7450f3-86f6-4f7d-94e4-6b18ee1c0d08" />
<div align="center">
 Bảng 3-1 : Biểu đồ đăng ký
</div>

# 2.5.2 Luồng xử lý mua vé
<img width="1068" height="789" alt="image" src="https://github.com/user-attachments/assets/914aebbd-383d-4d0b-ba48-667c8ab944a9" />
<div align="center">
 Bảng 3-2 : Biểu đồ mua vé
</div>

# 2.5.3 Luồng xử lý bán vé
<img width="1190" height="774" alt="image" src="https://github.com/user-attachments/assets/660e9b35-34fc-4768-8aa9-83ac1e039c0f" />
<div align="center">
 Bảng 3-2 : Biểu đồ bán vé
</div>

# 2.5.4 Luồng xử lý quản lý vé
<img width="1015" height="722" alt="image" src="https://github.com/user-attachments/assets/03266bb4-b98b-468b-aca5-33cb0d07c9ad" />
<div align="center">
 Bảng 3-3 : Biểu đồ quản lý vé
</div>

# 2.6 Thiết kế cơ sỡ dữ liệu
# 2.6.1 Mô hình ERD
<img width="1357" height="685" alt="image" src="https://github.com/user-attachments/assets/f7d0aaf8-b4a8-4eb9-8d44-6bf6bb53a509" />
<div align="center">
 Bảng 4 : Biểu đồ ERD
</div>

# 2.6.2 Mô hình cơ sở dữ liệu
<img width="883" height="735" alt="image" src="https://github.com/user-attachments/assets/c6710290-fa19-498b-909f-6d91a28e6fe0" />
<div align="center">
 Bảng 4-1 : Biểu đồ CSDL
</div>

# III. Yêu cầu phi chức năng
# 1. Hiệu suất 
- Thời gian tải trang & phản hồi API: không quá 3 giây thời gian phản hồi không quá 1 giây là hợp lý. Đặc biệt quan trọng trong các trang tìm kiếm sự kiện và chi tiết vé.

- Hỗ trợ đồng thời: ít nhất 30 người dùng là quá thấp. Một sự kiện có thể thu hút hàng nghìn hoặc chục nghìn người dùng đồng thời tại thời điểm mở bán hoặc ngay trước giờ diễn ra.

Đề xuất: Hệ thống phải chịu tải được ít nhất 5,000 người dùng đồng thời trong các thời điểm cao điểm (flash sale, sự kiện lớn). Cần có cơ chế "hàng đợi"  ảo để tránh sập hệ thống.

- Tối ưu hóa: Rất quan trọng. Bổ sung:

Cập nhật dữ liệu thời gian thực: Tình trạng vé (còn/hết), giá vé phải được cập nhật gần như ngay lập tức trên giao diện người dùng mà không cần tải lại trang để tránh trường hợp hai người cùng mua một vé.

Sử dụng CDN (Content Delivery Network) để phân phối hình ảnh, CSS, JS nhanh hơn trên toàn cầu.

# 2. Bảo mật 
- Mã hóa dữ liệu nhạy cảm: Bắt buộc. Không chỉ là mật khẩu, mà còn là thông tin thanh toán, thông tin cá nhân (CCCD/Passport nếu có yêu cầu xác thực).

- Chống tấn công SQL Injection, XSS: Cơ bản và bắt buộc.

- Logging: Cần ghi log chi tiết các hoạt động:

Giao dịch tài chính (mua, bán, rút tiền).

Thay đổi thông tin vé (giá, số lượng).

Đăng nhập, đăng xuất, các lần thử đăng nhập thất bại.

- Backup dữ liệu: Rất quan trọng.

- Bảo mật giao dịch: Tuân thủ tiêu chuẩn PCI DSS ( Payment Card Industry Data Security Standard) nếu trực tiếp xử lý thông tin thẻ tín dụng. Tích hợp với các cổng thanh toán uy tín (PayPal, Momo, VNPAY...) để giảm thiểu rủi ro.

- Chống gian lận:

Hệ thống cần có cơ chế phát hiện các hành vi đáng ngờ 

Xác thực người bánđể tăng độ tin cậy.

Xác thực vé: Nếu có thể, tích hợp API với nhà tổ chức sự kiện để kiểm tra tính hợp lệ của mã vạch/QR code của vé.

# 3. Khả năng mở rộng
- Kiến trúc module hóa: Rất tốt. Ví dụ: module quản lý người dùng, module quản lý sự kiện, module thanh toán, module tìm kiếm.

- Khả năng tích hợp: Cần xác định rõ các hệ thống cần tích hợp:

Bắt buộc: Cổng thanh toán, Dịch vụ email/SMS (để gửi thông báo, mã OTP).

Nên có: Nền tảng mạng xã hội (để đăng nhập/chia sẻ), Google Maps (hiển thị địa điểm), Dịch vụ phân tích (Google Analytics).

- Documentation: Cần có API documentation rõ ràng cho cả việc bảo trì nội bộ và tích hợp bên ngoài trong tương lai.

# 4. Giao diện người dùng (UI/UX)
- Thiết kế : Bắt buộc. Phần lớn người dùng sẽ truy cập qua di động và máy tính

- Thời gian học sử dụng: Không quá 30 phút  là một mục tiêu tốt. Quy trình mua vé và đăng bán vé phải cực kỳ đơn giản và trực quan.

Luồng mua vé: Tìm kiếm -> Chọn vé -> Thanh toán -> Nhận vé. Chỉ nên có 3-4 bước.

Luồng bán vé: Đăng nhập -> Điền thông tin vé -> Đặt giá -> Đăng bán.

- Giao diện nhất quán: Rất tốt.

- Bổ sung:

Tìm kiếm và bộ lọc mạnh mẽ: Người dùng cần lọc sự kiện theo: Tên, địa điểm, ngày tháng, danh mục (nhạc, thể thao...), khoảng giá.

Hiển thị thông tin vé rõ ràng: Sơ đồ chỗ ngồi nếu có, vị trí (khu, hàng, ghế), các lưu ý đặc biệt (vé có tầm nhìn hạn chế, vé điện tử/vé cứng).

# 5. Tương thích 
Danh sách của bạn đã rất đầy đủ và chính xác. Tối ưu cho kết nối mạng chậm là một điểm cộng lớn, đặc biệt khi người dùng đang ở khu vực đông người, sóng yếu.

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

# IV. Công nghệ sử dụng
- Frontend: ReactJS JavaScript

- Backend: Flask Api , Python

- API: Sử dụng chuẩn TodoApi để giao tiếp giữa frontend và backend.

- Cơ sở dữ liệu: Sử dụng SQL Server để lưu trữ dữ liệu.

- Bảo mật: Sử dụng ……………. để xác thực người dùng.

- Thông báo: Sử dụng email để thông báo cho người dùng.

- Triển khai: Sử dụng Docker để đóng gói và triển khai ứng dụng.

- Quản lý mã nguồn: Sử dụng Git để quản lý mã nguồn và GitHub để lưu trữ ma nguồn.
  
# V. Mô hình kiến trúc hệ thống
# Mô hình kiến trúc
Mô hình kiến trúc của hệ thống sẽ bao gồm các thành phần sau:

Client: Giao diện người dùng, xây dựng bằng…………, kết nối với API để lấy dữ liệu.

Server: Dịch vụ API, xây dựng bằng ………..   sử dụng kiến trúc 3 lớp để xử lý logic.

Presentation: Xử lý các yêu cầu từ client, gọi các phương thức từ lớp Service.

Business Logic: Chứa logic xử lý chính của ứng dụng, gọi các phương thức từ lớp Repository.

Data Access: Tương tác với cơ sở dữ liệu, thực hiện các thao tác CRUD.

Database: Cơ sở dữ liệu SQL Server, lưu trữ thông tin người dùng, lịch hẹn, dịch vụ..

Sơ đồ:

 

 

Mô hình cơ sở dữ liệu
Cơ sở dữ liệu sẽ bao gồm các bảng sau:

Users: Lưu thông tin người dùng, bao gồm tên, email, mật khẩu, quyền...

Appointments: Lịch hẹn, bao gồm thông tin khách hàng, đặt vé, thời gian...

Services: Dịch vụ, bao gồm tên, mô tả, giá cả...

Member: ……….

Đặt vé: Thông tin đặt vé, bao gồm địa chỉ, số điện thoại, giờ mở cửa...

Sơ đồ CSDL:

 

Giao diện người dùng
Giao diện người dùng sẽ bao gồm các trang sau:

Trang chủ: Hiển thị thông tin đặt vé, các dịch vụ, đặt vé nổi bật.

Trang dịch vụ: Hiển thị danh sách dịch vụ, cho phép tìm kiếm và xem chi tiết.

Trang đặt lịch hẹn: Truy cập từ trang dịch vụ, cho phép chọn dịch vụ, đặt vé, ngày, giờ.

Trang cá nhân: Hiển thị thông tin cá nhân, cho phép cập nhật thông tin, đổi mật khẩu, quản lý lịch hẹn.

Trang quản lý: Dành cho nhân viên và quản lý, cho phép xem lịch hẹn, cập nhật trạng thái.
