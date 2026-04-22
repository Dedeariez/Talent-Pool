from dataclasses import dataclass


@dataclass(frozen=True)
class ClientProfile:
    client_rate_usd_per_min: float
    dubbing_rate_idr_per_min: int
    translate_rate_idr_per_min: int
    quality_deposit_pct: float = 0.0


CLIENT_PROFILES = {
    "SCOTT": ClientProfile(
        client_rate_usd_per_min=10.0,
        dubbing_rate_idr_per_min=100_000,
        translate_rate_idr_per_min=0,
        quality_deposit_pct=0.20,
    ),
    "Global 100": ClientProfile(
        client_rate_usd_per_min=7.5,
        dubbing_rate_idr_per_min=80_000,
        translate_rate_idr_per_min=15_000,
    ),
    "CCJK": ClientProfile(
        client_rate_usd_per_min=6.5,
        dubbing_rate_idr_per_min=75_000,
        translate_rate_idr_per_min=15_000,
    ),
}


def format_idr(value: float) -> str:
    return f"Rp{value:,.0f}".replace(",", ".")


def calculate_project(project_name: str, client_name: str, duration_minutes: float, usd_to_idr: float):
    profile = CLIENT_PROFILES[client_name]

    total_revenue_idr = duration_minutes * profile.client_rate_usd_per_min * usd_to_idr
    total_team_rate = profile.dubbing_rate_idr_per_min + profile.translate_rate_idr_per_min
    total_team_cost_idr = duration_minutes * total_team_rate

    if client_name == "SCOTT":
        quality_deposit_value = total_revenue_idr * profile.quality_deposit_pct
        net_revenue_after_deposit = total_revenue_idr - quality_deposit_value
        payment_schedule = "Net 60 + Holding 20%"
    else:
        quality_deposit_value = 0
        net_revenue_after_deposit = total_revenue_idr
        payment_schedule = "Net 30"

    margin_idr = net_revenue_after_deposit - total_team_cost_idr

    return {
        "Nama Proyek": project_name,
        "Klien": client_name,
        "Durasi (Menit)": duration_minutes,
        "Kurs USD/IDR": usd_to_idr,
        "Revenue Kotor (IDR)": total_revenue_idr,
        "Potongan Quality Deposit (IDR)": quality_deposit_value,
        "Revenue Bersih (IDR)": net_revenue_after_deposit,
        "Pengeluaran Tim (IDR)": total_team_cost_idr,
        "Margin Bersih (IDR)": margin_idr,
        "Jadwal Pembayaran": payment_schedule,
    }


def pick_client() -> str:
    clients = list(CLIENT_PROFILES.keys())
    while True:
        print("\nPilih Klien:")
        for i, client in enumerate(clients, start=1):
            print(f"{i}. {client}")

        choice = input("Masukkan angka klien (1-3): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(clients):
            return clients[int(choice) - 1]

        print("Input tidak valid. Coba lagi.")


def main():
    print("=== Sistem Perhitungan Keuangan KV Voice Studio ===")
    print("Default kurs USD/IDR = 16000")

    projects = []

    while True:
        project_name = input("\nNama Proyek: ").strip()
        client_name = pick_client()

        duration_minutes = float(input("Durasi Total (menit): ").strip())
        kurs_input = input("Kurs USD ke IDR (Enter untuk default 16000): ").strip()
        usd_to_idr = float(kurs_input) if kurs_input else 16_000

        result = calculate_project(project_name, client_name, duration_minutes, usd_to_idr)
        projects.append(result)

        print("\n--- Hasil Kalkulasi Proyek ---")
        print(f"Nama Proyek                     : {result['Nama Proyek']}")
        print(f"Klien                           : {result['Klien']}")
        print(f"Durasi (Menit)                  : {result['Durasi (Menit)']}")
        print(f"Revenue Kotor (IDR)             : {format_idr(result['Revenue Kotor (IDR)'])}")
        print(
            "Potongan Quality Deposit (IDR)   : "
            f"{format_idr(result['Potongan Quality Deposit (IDR)'])}"
        )
        print(f"Revenue Bersih (IDR)            : {format_idr(result['Revenue Bersih (IDR)'])}")
        print(f"Total Pengeluaran Tim (IDR)     : {format_idr(result['Pengeluaran Tim (IDR)'])}")
        print(f"Margin Bersih (IDR)             : {format_idr(result['Margin Bersih (IDR)'])}")
        print(f"Jadwal Pembayaran               : {result['Jadwal Pembayaran']}")

        more = input("\nTambah proyek lain? (y/n): ").strip().lower()
        if more != "y":
            break

    total_margin = sum(row["Margin Bersih (IDR)"] for row in projects)
    total_revenue = sum(row["Revenue Bersih (IDR)"] for row in projects)
    total_expense = sum(row["Pengeluaran Tim (IDR)"] for row in projects)

    print("\n=== Ringkasan Semua Proyek ===")
    print(f"Jumlah Proyek                   : {len(projects)}")
    print(f"Total Revenue Bersih (IDR)      : {format_idr(total_revenue)}")
    print(f"Total Pengeluaran Tim (IDR)     : {format_idr(total_expense)}")
    print(f"Total Margin Bersih (IDR)       : {format_idr(total_margin)}")


if __name__ == "__main__":
    main()
