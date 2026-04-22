from dataclasses import dataclass


@dataclass(frozen=True)
class ClientProfile:
    client_rate_usd_per_min: float
    dubbing_rate_idr_per_min: int
    translate_rate_idr_per_min: int
    qc_rate_idr_per_min: int
    quality_deposit_pct: float = 0.0


CLIENT_PROFILES = {
    "SCOTT": ClientProfile(
        client_rate_usd_per_min=10.0,
        dubbing_rate_idr_per_min=100_000,
        translate_rate_idr_per_min=0,
        qc_rate_idr_per_min=100_000,
        quality_deposit_pct=0.20,
    ),
    "Global 100": ClientProfile(
        client_rate_usd_per_min=7.5,
        dubbing_rate_idr_per_min=80_000,
        translate_rate_idr_per_min=15_000,
        qc_rate_idr_per_min=80_000,
    ),
    "CCJK": ClientProfile(
        client_rate_usd_per_min=6.5,
        dubbing_rate_idr_per_min=75_000,
        translate_rate_idr_per_min=15_000,
        qc_rate_idr_per_min=75_000,
    ),
    "Shirley Vdus": ClientProfile(
        client_rate_usd_per_min=10.0,
        dubbing_rate_idr_per_min=100_000,
        translate_rate_idr_per_min=0,
        qc_rate_idr_per_min=100_000,
    ),
}


def format_idr(value: float) -> str:
    return f"Rp{value:,.0f}".replace(",", ".")


def paypal_rate(usd_amount: float) -> float:
    if usd_amount <= 3_000:
        return 0.044
    if usd_amount <= 10_000:
        return 0.039
    if usd_amount <= 100_000:
        return 0.037
    return 0.034


def calculate_paypal_fee(usd_amount: float) -> tuple[float, float]:
    pct = paypal_rate(usd_amount)
    fee_usd = (usd_amount * pct) + 0.30
    return pct, fee_usd


def calculate_project(
    project_name: str,
    client_name: str,
    dubbing_minutes: float,
    qc_minutes: float,
    translate_minutes: float,
    usd_to_idr: float,
):
    profile = CLIENT_PROFILES[client_name]

    total_minutes = dubbing_minutes + qc_minutes + translate_minutes
    total_revenue_usd = total_minutes * profile.client_rate_usd_per_min
    total_revenue_idr = total_revenue_usd * usd_to_idr

    paypal_pct, paypal_fee_usd = calculate_paypal_fee(total_revenue_usd)
    paypal_fee_idr = paypal_fee_usd * usd_to_idr

    dubbing_cost_idr = dubbing_minutes * profile.dubbing_rate_idr_per_min
    qc_cost_idr = qc_minutes * profile.qc_rate_idr_per_min
    translate_cost_idr = translate_minutes * profile.translate_rate_idr_per_min

    transfer_teh_ocha = dubbing_cost_idr + qc_cost_idr
    transfer_annieda = translate_cost_idr
    total_team_cost_idr = transfer_teh_ocha + transfer_annieda

    if client_name == "SCOTT":
        quality_deposit_value = total_revenue_idr * profile.quality_deposit_pct
        payment_schedule = "Net 60 + Holding 20%"
    else:
        quality_deposit_value = 0
        payment_schedule = "Net 30"

    net_revenue_after_cuts = total_revenue_idr - paypal_fee_idr - quality_deposit_value
    margin_idr = net_revenue_after_cuts - total_team_cost_idr

    return {
        "Nama Proyek": project_name,
        "Klien": client_name,
        "Durasi Dubbing (Menit)": dubbing_minutes,
        "Durasi QC (Menit)": qc_minutes,
        "Durasi Translate (Menit)": translate_minutes,
        "Total Durasi (Menit)": total_minutes,
        "Kurs USD/IDR": usd_to_idr,
        "Tagihan ke Klien (USD)": total_revenue_usd,
        "Tagihan ke Klien (IDR)": total_revenue_idr,
        "Biaya PayPal %": paypal_pct,
        "Biaya PayPal (USD)": paypal_fee_usd,
        "Biaya PayPal (IDR)": paypal_fee_idr,
        "Potongan Quality Deposit (IDR)": quality_deposit_value,
        "Pendapatan Bersih Setelah Potongan (IDR)": net_revenue_after_cuts,
        "Transfer Teh Ocha - Dubbing+QC (IDR)": transfer_teh_ocha,
        "Transfer Annieda - Translate (IDR)": transfer_annieda,
        "Total Transfer Tim (IDR)": total_team_cost_idr,
        "Margin Bersih (IDR)": margin_idr,
        "Jadwal Pembayaran": payment_schedule,
    }


def pick_client() -> str:
    clients = list(CLIENT_PROFILES.keys())
    while True:
        print("\nPilih Klien:")
        for i, client in enumerate(clients, start=1):
            print(f"{i}. {client}")

        choice = input(f"Masukkan angka klien (1-{len(clients)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(clients):
            return clients[int(choice) - 1]

        print("Input tidak valid. Coba lagi.")


def main():
    print("=== Sistem Perhitungan Keuangan KV Voice Studio ===")
    print("Default kurs USD/IDR = 16000")
    print("Fee PayPal otomatis: 4.4%/3.9%/3.7%/3.4% + USD 0.30 per transaksi")

    projects = []

    while True:
        project_name = input("\nNama Proyek: ").strip()
        client_name = pick_client()

        dubbing_minutes = float(input("Durasi Dubbing (menit): ").strip() or 0)
        qc_minutes = float(input("Durasi QC (menit): ").strip() or 0)
        translate_minutes = float(input("Durasi Translate (menit): ").strip() or 0)

        kurs_input = input("Kurs USD ke IDR (Enter untuk default 16000): ").strip()
        usd_to_idr = float(kurs_input) if kurs_input else 16_000

        result = calculate_project(
            project_name,
            client_name,
            dubbing_minutes,
            qc_minutes,
            translate_minutes,
            usd_to_idr,
        )
        projects.append(result)

        print("\n--- Hasil Kalkulasi Proyek ---")
        print(f"Nama Proyek                                : {result['Nama Proyek']}")
        print(f"Klien                                      : {result['Klien']}")
        print(f"Tagihan ke Klien (USD)                     : ${result['Tagihan ke Klien (USD)']:,.2f}")
        print(f"Tagihan ke Klien (IDR)                     : {format_idr(result['Tagihan ke Klien (IDR)'])}")
        print(
            "Biaya PayPal                                : "
            f"{result['Biaya PayPal %'] * 100:.1f}% + $0.30 = ${result['Biaya PayPal (USD)']:,.2f} "
            f"({format_idr(result['Biaya PayPal (IDR)'])})"
        )
        print(
            "Potongan Quality Deposit (IDR)              : "
            f"{format_idr(result['Potongan Quality Deposit (IDR)'])}"
        )
        print(
            "Pendapatan Bersih Setelah Potongan (IDR)    : "
            f"{format_idr(result['Pendapatan Bersih Setelah Potongan (IDR)'])}"
        )
        print(
            "Transfer Teh Ocha (Dubbing+QC)              : "
            f"{format_idr(result['Transfer Teh Ocha - Dubbing+QC (IDR)'])}"
        )
        print(
            "Transfer Annieda (Translate)                : "
            f"{format_idr(result['Transfer Annieda - Translate (IDR)'])}"
        )
        print(f"Total Transfer Tim (IDR)                    : {format_idr(result['Total Transfer Tim (IDR)'])}")
        print(f"Margin Bersih (IDR)                         : {format_idr(result['Margin Bersih (IDR)'])}")
        print(f"Jadwal Pembayaran                           : {result['Jadwal Pembayaran']}")

        more = input("\nTambah proyek lain? (y/n): ").strip().lower()
        if more != "y":
            break

    total_margin = sum(row["Margin Bersih (IDR)"] for row in projects)
    total_team_transfer = sum(row["Total Transfer Tim (IDR)"] for row in projects)
    total_transfer_ocha = sum(row["Transfer Teh Ocha - Dubbing+QC (IDR)"] for row in projects)
    total_transfer_annieda = sum(row["Transfer Annieda - Translate (IDR)"] for row in projects)

    print("\n=== Ringkasan Semua Proyek ===")
    print(f"Jumlah Proyek                               : {len(projects)}")
    print(f"Total Transfer Teh Ocha (IDR)              : {format_idr(total_transfer_ocha)}")
    print(f"Total Transfer Annieda (IDR)               : {format_idr(total_transfer_annieda)}")
    print(f"Total Transfer Tim (IDR)                   : {format_idr(total_team_transfer)}")
    print(f"Total Margin Bersih (IDR)                  : {format_idr(total_margin)}")

    print("\n=== Rekap Tagihan per Klien ===")
    client_totals: dict[str, float] = {}
    for row in projects:
        client = str(row["Klien"])
        client_totals[client] = client_totals.get(client, 0) + float(row["Tagihan ke Klien (IDR)"])

    for client, total in client_totals.items():
        print(f"{client:<40}: {format_idr(total)}")


if __name__ == "__main__":
    main()
