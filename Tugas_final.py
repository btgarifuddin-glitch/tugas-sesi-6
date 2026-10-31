
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# ==========================================
# 1. KONFIGURASI DATABASE
# ==========================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "siakad",
    "port": 3306
}

TABLES = {
    "dosen": "Data Dosen",
    "mahasiswa": "Data Mahasiswa",
    "jadwal_kuliah": "Jadwal Kuliah",
    "krs": "Kartu Rencana Studi",
    "matakuliah": "Mata Kuliah",
    "pembayaran_ukt": "Pembayaran UKT"
}


def koneksi():
    return mysql.connector.connect(**DB_CONFIG)


# ==========================================
# 2. TAMPILAN DAN WARNA
# ==========================================

BG = "#F1F5F9"
NAVY = "#172554"
BLUE = "#2563EB"
WHITE = "#FFFFFF"
TEXT = "#1E293B"
GREEN = "#16A34A"
RED = "#DC2626"


# ==========================================
# 3. APLIKASI UTAMA
# ==========================================

class SiakadApp:

    def __init__(self, root):
        self.root = root
        self.root.title("SIAKAD - Sistem Informasi Akademik")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        self.current_table = None
        self.columns = []
        self.primary_key = None

        self.tampilan_login()

    # ======================================
    # 4. HALAMAN LOGIN
    # ======================================

    def tampilan_login(self):
        self.bersihkan()

        frame = tk.Frame(self.root, bg=WHITE, padx=45, pady=40)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame, text="SIAKAD",
            font=("Arial", 28, "bold"),
            bg=WHITE, fg=NAVY
        ).pack(pady=(0, 5))

        tk.Label(
            frame, text="Sistem Informasi Akademik",
            font=("Arial", 11),
            bg=WHITE, fg="#64748B"
        ).pack(pady=(0, 25))

        tk.Label(
            frame, text="Nomor Induk Pegawai (NIP)",
            bg=WHITE, fg=TEXT
        ).pack(anchor="w")

        self.entry_nip = ttk.Entry(frame, width=38)
        self.entry_nip.pack(pady=(5, 15), ipady=6)

        tk.Label(
            frame, text="Email",
            bg=WHITE, fg=TEXT
        ).pack(anchor="w")

        self.entry_email = ttk.Entry(
            frame, width=38, show="*"
        )
        self.entry_email.pack(pady=(5, 20), ipady=6)

        ttk.Button(
            frame, text="LOGIN",
            command=self.login
        ).pack(fill="x", ipady=7)

        tk.Label(
            frame,
            text="SIAKAD © 2026",
            bg=WHITE, fg="#94A3B8"
        ).pack(pady=(20, 0))

        self.entry_nip.focus()

    def login(self):
        nip = self.entry_nip.get().strip()
        email = self.entry_email.get().strip()

        if not nip or not email:
            messagebox.showwarning(
                "Peringatan", "NIP dan Email harus diisi!"
            )
            return

        try:
            db = koneksi()
            cursor = db.cursor()

            cursor.execute(
                """
                SELECT nip, nama_dosen
                FROM dosen
                WHERE nip = %s AND email = %s
                """,
                (nip, email)
            )

            data = cursor.fetchone()
            cursor.close()
            db.close()

            if data:
                self.nama_user = data[1]
                self.tampilan_dashboard()
            else:
                messagebox.showerror(
                    "Login Gagal",
                    "NIP atau Email tidak sesuai!"
                )

        except Error as e:
            messagebox.showerror(
                "Database Error", str(e)
            )

    # ======================================
    # 5. DASHBOARD
    # ======================================

    def tampilan_dashboard(self):
        self.bersihkan()

        header = tk.Frame(self.root, bg=NAVY, height=75)
        header.pack(fill="x")

        tk.Label(
            header, text="SIAKAD",
            font=("Arial", 21, "bold"),
            bg=NAVY, fg=WHITE
        ).pack(side="left", padx=25, pady=18)

        tk.Label(
            header,
            text=f"Selamat Datang, {self.nama_user}",
            font=("Arial", 11),
            bg=NAVY, fg=WHITE
        ).pack(side="right", padx=25)

        content = tk.Frame(self.root, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=25)

        tk.Label(
            content, text="Dashboard Akademik",
            font=("Arial", 23, "bold"),
            bg=BG, fg=TEXT
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Pilih tabel yang ingin kamu kelola.",
            font=("Arial", 11),
            bg=BG, fg="#64748B"
        ).pack(anchor="w", pady=(5, 20))

        cards = tk.Frame(content, bg=BG)
        cards.pack(fill="both", expand=True)

        for i, (table, nama) in enumerate(TABLES.items()):
            row = i // 3
            col = i % 3

            card = tk.Frame(
                cards, bg=WHITE,
                highlightbackground="#E2E8F0",
                highlightthickness=1
            )
            card.grid(
                row=row, column=col,
                padx=10, pady=10,
                sticky="nsew"
            )

            cards.grid_columnconfigure(col, weight=1)
            cards.grid_rowconfigure(row, weight=1)

            tk.Label(
                card, text=nama,
                font=("Arial", 14, "bold"),
                bg=WHITE, fg=NAVY
            ).pack(pady=(25, 8))

            jumlah = self.hitung_data(table)

            tk.Label(
                card,
                text=f"{jumlah} Data",
                font=("Arial", 11),
                bg=WHITE, fg="#64748B"
            ).pack(pady=5)

            ttk.Button(
                card, text="BUKA TABEL",
                command=lambda t=table: self.buka_tabel(t)
            ).pack(pady=(10, 25), padx=20, fill="x")

        ttk.Button(
            content, text="LOGOUT",
            command=self.tampilan_login
        ).pack(anchor="e", pady=10)

    def hitung_data(self, table):
        try:
            db = koneksi()
            cursor = db.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM `{table}`")
            jumlah = cursor.fetchone()[0]
            cursor.close()
            db.close()
            return jumlah
        except Error:
            return 0

    # ======================================
    # 6. HALAMAN TABEL
    # ======================================

    def buka_tabel(self, table):
        self.current_table = table
        self.bersihkan()

        try:
            db = koneksi()
            cursor = db.cursor()

            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            self.columns = cursor.fetchall()

            cursor.execute(
                f"SHOW KEYS FROM `{table}` WHERE Key_name='PRIMARY'"
            )
            keys = cursor.fetchall()

            self.primary_key = keys[0][4] if len(keys) == 1 else None

            cursor.close()
            db.close()

        except Error as e:
            messagebox.showerror("Error", str(e))
            self.tampilan_dashboard()
            return

        header = tk.Frame(self.root, bg=NAVY)
        header.pack(fill="x")

        tk.Label(
            header, text=TABLES[table],
            font=("Arial", 20, "bold"),
            bg=NAVY, fg=WHITE
        ).pack(side="left", padx=25, pady=18)

        ttk.Button(
            header, text="KEMBALI",
            command=self.tampilan_dashboard
        ).pack(side="right", padx=20, pady=15)

        content = tk.Frame(self.root, bg=BG)
        content.pack(fill="both", expand=True, padx=25, pady=20)

        tools = tk.Frame(content, bg=BG)
        tools.pack(fill="x", pady=(0, 15))

        self.search_var = tk.StringVar()

        ttk.Entry(
            tools, textvariable=self.search_var,
            width=35
        ).pack(side="left", ipady=5)

        ttk.Button(
            tools, text="CARI",
            command=self.cari_data
        ).pack(side="left", padx=5)

        ttk.Button(
            tools, text="TAMPILKAN SEMUA",
            command=self.muat_data
        ).pack(side="left", padx=5)

        ttk.Button(
            tools, text="TAMBAH DATA",
            command=lambda: self.form_data("tambah")
        ).pack(side="right", padx=5)

        ttk.Button(
            tools, text="EDIT DATA",
            command=lambda: self.form_data("edit")
        ).pack(side="right", padx=5)

        ttk.Button(
            tools, text="HAPUS DATA",
            command=self.hapus_data
        ).pack(side="right", padx=5)

        # Tabel data
        table_frame = tk.Frame(content, bg=WHITE)
        table_frame.pack(fill="both", expand=True)

        names = [col[0] for col in self.columns]

        self.tree = ttk.Treeview(
            table_frame,
            columns=names,
            show="headings"
        )

        for name in names:
            self.tree.heading(name, text=name.upper())
            self.tree.column(name, width=150, anchor="center")

        scroll_y = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.tree.yview
        )

        scroll_x = ttk.Scrollbar(
            table_frame, orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )

        self.tree.pack(
            side="top", fill="both", expand=True
        )
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")

        self.muat_data()

    # ======================================
    # 7. MENAMPILKAN DATA
    # ======================================

    def muat_data(self, keyword=None):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            db = koneksi()
            cursor = db.cursor()

            if keyword:
                conditions = " OR ".join(
                    f"CAST(`{col[0]}` AS CHAR) LIKE %s"
                    for col in self.columns
                )

                sql = (
                    f"SELECT * FROM `{self.current_table}` "
                    f"WHERE {conditions}"
                )

                values = tuple(
                    [f"%{keyword}%"] * len(self.columns)
                )

                cursor.execute(sql, values)

            else:
                cursor.execute(
                    f"SELECT * FROM `{self.current_table}`"
                )

            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)

            cursor.close()
            db.close()

        except Error as e:
            messagebox.showerror("Error", str(e))

    def cari_data(self):
        keyword = self.search_var.get().strip()

        if not keyword:
            self.muat_data()
        else:
            self.muat_data(keyword)

    # ======================================
    # 8. FORM TAMBAH DAN EDIT
    # ======================================

    def form_data(self, mode):
        selected = self.tree.selection()

        if mode == "edit" and not selected:
            messagebox.showwarning(
                "Peringatan", "Pilih data terlebih dahulu!"
            )
            return

        if mode == "edit" and not self.primary_key:
            messagebox.showerror(
                "Peringatan",
                "Tabel harus memiliki satu PRIMARY KEY untuk diedit."
            )
            return

        old_values = (
            self.tree.item(selected[0])["values"]
            if selected else None
        )

        form = tk.Toplevel(self.root)
        form.title("Form Data")
        form.geometry("450x600")
        form.configure(bg=WHITE)
        form.grab_set()

        tk.Label(
            form,
            text="Tambah Data" if mode == "tambah" else "Edit Data",
            font=("Arial", 18, "bold"),
            bg=WHITE, fg=NAVY
        ).pack(pady=20)

        fields = {}

        for i, col in enumerate(self.columns):
            name = col[0]
            extra = str(col[6]).lower()

            if mode == "tambah" and "auto_increment" in extra:
                continue

            tk.Label(
                form, text=name,
                bg=WHITE, fg=TEXT
            ).pack(anchor="w", padx=30)

            entry = ttk.Entry(form, width=45)
            entry.pack(padx=30, pady=(3, 10), ipady=5)

            if mode == "edit":
                entry.insert(0, str(old_values[i]))

            fields[name] = entry

        def simpan():
            try:
                db = koneksi()
                cursor = db.cursor()

                names = list(fields.keys())
                values = [fields[n].get().strip() for n in names]

                if any(v == "" for v in values):
                    messagebox.showwarning(
                        "Peringatan",
                        "Semua kolom harus diisi!"
                    )
                    cursor.close()
                    db.close()
                    return

                if mode == "tambah":
                    kolom = ", ".join(f"`{n}`" for n in names)
                    tanda = ", ".join(["%s"] * len(names))

                    sql = (
                        f"INSERT INTO `{self.current_table}` "
                        f"({kolom}) VALUES ({tanda})"
                    )

                    cursor.execute(sql, tuple(values))

                else:
                    pk_index = names.index(self.primary_key)
                    pk_value = old_values[
                        next(
                            i for i, c in enumerate(self.columns)
                            if c[0] == self.primary_key
                        )
                    ]

                    update_names = [
                        n for n in names
                        if n != self.primary_key
                    ]

                    if not update_names:
                        messagebox.showwarning(
                            "Peringatan", "Tidak ada kolom untuk diubah."
                        )
                        cursor.close()
                        db.close()
                        return

                    set_sql = ", ".join(
                        f"`{n}`=%s" for n in update_names
                    )

                    update_values = [
                        fields[n].get().strip()
                        for n in update_names
                    ]

                    sql = (
                        f"UPDATE `{self.current_table}` "
                        f"SET {set_sql} "
                        f"WHERE `{self.primary_key}`=%s"
                    )

                    cursor.execute(
                        sql, tuple(update_values + [pk_value])
                    )

                db.commit()
                cursor.close()
                db.close()

                messagebox.showinfo(
                    "Berhasil", "Data berhasil disimpan!"
                )

                form.destroy()
                self.muat_data()

            except Error as e:
                messagebox.showerror("Database Error", str(e))

        ttk.Button(
            form, text="SIMPAN",
            command=simpan
        ).pack(pady=20, ipadx=30, ipady=5)

    # ======================================
    # 9. HAPUS DATA
    # ======================================

    def hapus_data(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning(
                "Peringatan", "Pilih data yang ingin dihapus!"
            )
            return

        if not self.primary_key:
            messagebox.showerror(
                "Peringatan",
                "Tabel tidak memiliki satu PRIMARY KEY."
            )
            return

        yakin = messagebox.askyesno(
            "Konfirmasi",
            "Apakah kamu yakin ingin menghapus data ini?"
        )

        if not yakin:
            return

        try:
            values = self.tree.item(selected[0])["values"]

            pk_index = next(
                i for i, col in enumerate(self.columns)
                if col[0] == self.primary_key
            )

            pk_value = values[pk_index]

            db = koneksi()
            cursor = db.cursor()

            cursor.execute(
                f"DELETE FROM `{self.current_table}` "
                f"WHERE `{self.primary_key}`=%s",
                (pk_value,)
            )

            db.commit()
            cursor.close()
            db.close()

            messagebox.showinfo(
                "Berhasil", "Data berhasil dihapus!"
            )

            self.muat_data()

        except Error as e:
            messagebox.showerror(
                "Gagal Menghapus",
                "Data tidak dapat dihapus.\n"
                "Kemungkinan data masih digunakan oleh tabel lain.\n\n"
                + str(e)
            )

    # ======================================
    # 10. MEMBERSIHKAN HALAMAN
    # ======================================

    def bersihkan(self):
        for widget in self.root.winfo_children():
            widget.destroy()


# ==========================================
# 11. MENJALANKAN APLIKASI
# ==========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = SiakadApp(root)
    root.mainloop()
