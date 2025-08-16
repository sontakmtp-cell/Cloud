# core/utils.py
# -*- coding: utf-8 -*-
import math
from typing import Tuple, Dict

def deg2rad(d: float) -> float:
    return float(d) * math.pi / 180.0

def parse_trough_label(label: str, default_deg: float = 20.0) -> float:
    if not label:
        return default_deg
    try:
        import re
        m = re.search(r"(\d+(\.\d+)?)", str(label))
        return float(m.group(1)) if m else default_deg
    except Exception:
        return default_deg

# --- [BẮT ĐẦU NÂNG CẤP] ---
# Bảng 4: Hệ số K tính toán mặt cắt dòng chảy (số hóa từ PDF)
# Dùng cho băng tải máng 3 con lăn.
K_FACTOR_TABLE_3_ROLL: Dict[int, Dict[int, float]] = {
    # góc máng -> {góc mái -> K}
    10: {10: 0.0649, 20: 0.0945, 30: 0.1253},
    15: {10: 0.0817, 20: 0.1106, 30: 0.1408}, # Note: PDF có thể in nhầm thứ tự 10,20
    20: {10: 0.0963, 20: 0.1245, 30: 0.1538},
    25: {10: 0.1113, 20: 0.1381, 30: 0.1661}, # Note: PDF có thể in nhầm thứ tự 10,20
    30: {10: 0.1232, 20: 0.1488, 30: 0.1754},
    35: {10: 0.1348, 20: 0.1588, 30: 0.1837},
    40: {10: 0.1426, 20: 0.1649, 30: 0.1882},
    45: {10: 0.1500, 20: 0.1704, 30: 0.1916}, # Note: PDF có thể in nhầm thứ tự 10,20
}
# Băng phẳng
K_FACTOR_TABLE_FLAT: Dict[int, float] = {10: 0.0295, 20: 0.0591, 30: 0.0906}


def _interpolate_k(angle: float, k_map: Dict[int, float]) -> float:
    """Nội suy tuyến tính giá trị K từ một map."""
    keys = sorted(k_map.keys())
    if angle <= keys[0]:
        return k_map[keys[0]]
    if angle >= keys[-1]:
        return k_map[keys[-1]]
    for i in range(len(keys) - 1):
        if keys[i] <= angle <= keys[i+1]:
            x0, y0 = keys[i], k_map[keys[i]]
            x1, y1 = keys[i+1], k_map[keys[i+1]]
            return y0 + (y1 - y0) * (angle - x0) / (x1 - x0)
    return k_map[keys[len(keys) // 2]] # Fallback

def get_k_factor(trough_deg: float, surcharge_deg: float) -> float:
    """
    Tra cứu hệ số K từ Bảng 4 trong PDF, có nội suy.
    """
    trough_deg = float(trough_deg)
    surcharge_deg = float(surcharge_deg)

    if trough_deg < 5: # Coi như băng phẳng
        return _interpolate_k(surcharge_deg, K_FACTOR_TABLE_FLAT)

    # Nội suy theo góc mái trước
    k_at_surcharge = {}
    trough_angles = sorted(K_FACTOR_TABLE_3_ROLL.keys())
    for t_ang in trough_angles:
        k_at_surcharge[t_ang] = _interpolate_k(surcharge_deg, K_FACTOR_TABLE_3_ROLL[t_ang])

    # Nội suy theo góc máng sau
    return _interpolate_k(trough_deg, k_at_surcharge)


def cross_section_area_m2(B_mm: int, trough_deg: float, surcharge_deg: float) -> float:
    """
    Tính diện tích mặt cắt ngang theo Công thức (3) và Bảng 4, trang 7, PDF.
    A = K * (0.9*B - 0.05)^2
    """
    B_m = max(0.3, float(B_mm) / 1000.0)
    K = get_k_factor(trough_deg, surcharge_deg)
    
    # Chiều rộng hiệu quả, không được nhỏ hơn 0
    effective_width_term = max(0, 0.9 * B_m - 0.05)
    
    return K * (effective_width_term ** 2)


def capacity_from_geometry_tph(B_mm: int, trough_deg: float, surcharge_deg: float,
                               V_mps: float, density_tpm3: float) -> Tuple[float, float]:
    """
    Tính lưu lượng dựa trên hình học theo Công thức (1), trang 6, PDF.
    Qt = 3600 * A * V * gamma (chuyển đổi từ công thức gốc)
    """
    A = cross_section_area_m2(B_mm, trough_deg, surcharge_deg)
    V = max(0.05, float(V_mps))
    rho = max(0.1, float(density_tpm3))
    
    # Công thức gốc: Qt (tấn/h) = 60 * A(m2) * V(m/phút) * rho(tấn/m3)
    # V(m/phút) = V(m/s) * 60
    # => Qt = 60 * A * (V_mps * 60) * rho = 3600 * A * V_mps * rho
    qt_calc = 3600 * A * V * rho
    return qt_calc, A
# --- [KẾT THÚC NÂNG CẤP] ---