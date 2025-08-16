# cloud.py
# -*- coding: utf-8 -*-
"""
Điểm vào ứng dụng (main).
File này khởi tạo và hiển thị màn hình đăng nhập trước khi vào cửa sổ chính.
"""
import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QDialog
# Import các cửa sổ cần thiết
from ui.main_window_3d_enhanced import Enhanced3DConveyorWindow
from ui.login_dialog import LoginDialog  # <<< THÊM DÒNG NÀY
from core.specs import VERSION
import logging

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Conveyor Calculator Professional")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("haingocson@gmail.com")

    # --- [BẮT ĐẦU THAY ĐỔI] ---
    # Hiển thị màn hình đăng nhập trước
    login_dialog = LoginDialog()
    
    # exec() sẽ khóa chương trình cho đến khi dialog được đóng
    # và trả về kết quả (Accepted hoặc Rejected)
    result = login_dialog.exec()

    # Chỉ khi đăng nhập thành công (Accepted) thì mới tiếp tục
    if result == QDialog.Accepted:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("conveyor_calculator.log", encoding="utf-8"),]
        )

        try:
            # Tạo và hiển thị cửa sổ chính của ứng dụng
            main_window = Enhanced3DConveyorWindow()
            main_window.show()
            return app.exec()
        except Exception as e:
            QMessageBox.critical(None, "Lỗi khởi động", f"Không thể khởi động ứng dụng chính:\n{e}")
            logging.error(f"Lỗi khởi động cửa sổ chính: {e}", exc_info=True)
            return 1
    else:
        # Nếu người dùng đóng cửa sổ đăng nhập hoặc đăng nhập thất bại,
        # chương trình sẽ thoát một cách êm ái.
        return 0
    # --- [KẾT THÚC THAY ĐỔI] ---

if __name__ == "__main__":
    sys.exit(main())
