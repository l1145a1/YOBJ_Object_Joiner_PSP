import struct
import sys
import os
import tkinter as tk
from tkinter import filedialog, messagebox

FILE_HEADER = 8
base_mesh_object_offset = []
base_mesh_texture_count = []
base_mesh_vertice_header_1_offset = []
base_mesh_texture_offset = []
base_mesh_vertice_header_2_offset = []
base_mesh_vertice_count = []
mesh_block_offset=[]
mesh_header=[]

def out(p, cursor, diff):   #pofo encrpyt logic
    count = 0
    sp = cursor - diff
    if sp <= 0xFC:
        sp = (sp >> 2) | 0x40
        p.write(struct.pack('B', sp))
        count += 1
    elif sp <= 0xFFFC:
        sp = (sp >> 2) | 0x8000
        sp = struct.pack('>H', sp)
        p.write(sp)
        count += 2
    else:
        sp = (sp >> 2) | 0xC0000000
        sp = struct.pack('>I', sp)
        p.write(sp)
        count += 4
    return count

def generate_pof0(f):
    vertex_offset =[]
    UV_offset=[]
    texture_offset=[]
    texture_count=[]
    all_offset=[]
    f.seek(0, os.SEEK_END)
    byte_count = 0
    word = b'POF0'
    f.write(word)
    pof0_count_offset=f.tell()
    f.write(struct.pack('<I', byte_count))
    start_pof0=f.tell()
    f.seek(0)
    word = f.read(4).decode('ascii')
    if word != "YOBJ":
        print("Invalid YOBJ file, JBOY header missing")
        return

    pof0_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, POF0 Offset: {pof0_offset}")
    temp = struct.unpack('<I', f.read(4))[0]  # zero
    temp = struct.unpack('<I', f.read(4))[0]  # pof0 offset again
    print(f"Read Offset {f.tell()-4}, POF02 Offset: {temp}")
    if temp != pof0_offset:
        print("Invalid YOBJ file, second pof0 offset different from first")
        return

    f.read(8)  # skip two zeros
    mesh_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Mesh Count: {mesh_count}")

    f.read(8)
    cursor = f.tell()
    all_offset.append(FILE_HEADER)
    all_offset.append(f.tell())
    mesh_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Mesh Offset: {mesh_offset}")

    f.seek(-12,1)
    bone_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Bone Count: {bone_count}")

    tex_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Texture Count: {tex_count}")

    f.read(4)
    temp = cursor
    cursor = f.tell()
    all_offset.append(f.tell())

    bone_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Bone Offset: {bone_offset}")

    temp = cursor
    cursor = f.tell()
    all_offset.append(f.tell())

    texname_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Texture Name Offset: {texname_offset}")

    temp = cursor
    cursor = f.tell()
    all_offset.append(f.tell())

    obj_groupname_offset = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Object Groupname Offset: {obj_groupname_offset}")

    obj_group_count = struct.unpack('<I', f.read(4))[0]
    print(f"Read Offset {f.tell()-4}, Object Group Count: {obj_group_count}")

    f.seek(mesh_offset)

    for i in range(mesh_count):
        description_offset = f.tell();
        print   (f"Object {i} Offset {f.tell()}")
        f.read(12)  # skip two zeros
        temp1 = struct.unpack('<I', f.read(4))[0]
        texture_count.append(temp1)
        print(f"Read Offset {f.tell()-4}, Texture Count: {temp1}")

        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        vertex_offset.append(temp1)
        print(f"Read Offset {f.tell()-4}, Vertex Offset: {temp1}")

        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        texture_offset.append(temp1)
        print(f"Read Offset {f.tell()-4}, Texture Offset: {temp1}")

        f.read(8)
        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        UV_offset.append(temp1)
        print(f"Read Offset {f.tell()-4}, UV Offset: {temp1}")
        f.read(28)

    for i in range(mesh_count):
        print(f"Object {i} More Detail")

        f.seek(vertex_offset[i]+16)
        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        print(f"Read Offset {f.tell()-4}, Vertex Offset 2: {temp1}")

        f.seek(UV_offset[i]+8)
        temp = cursor
        cursor = f.tell()
        all_offset.append(f.tell())

        temp1 = struct.unpack('<I', f.read(4))[0]
        print(f"Read Offset {f.tell()-4}, UV Offset 2: {temp1}")

        f.seek(texture_offset[i]+140)
        mesh_size=[]
        mesh_offset_a=[]
        for j in range(texture_count[i]):
            print(f"Texture: {j}")

            temp1 = struct.unpack('<I', f.read(4))[0]
            mesh_size.append(temp1)
            print(f"Read Offset {f.tell()-4}, Mesh Size: {temp1}")

            temp = cursor
            cursor = f.tell()
            all_offset.append(f.tell())

            temp1 = struct.unpack('<I', f.read(4))[0]
            mesh_offset_a.append(temp1)
            print(f"Read Offset {f.tell()-4}, Texture Offset A: {temp1}")

            temp = cursor
            cursor = f.tell()
            all_offset.append(f.tell())

            temp1 = struct.unpack('<I', f.read(4))[0]
            print(f"Read Offset {f.tell()-4}, Texture Offset B : {temp1}")
            f.read(132)
        print(mesh_offset_a)
        for j in range(texture_count[i]):
            f.seek(mesh_offset_a[j]+20)
            for k in range(mesh_size[j]):
                temp = cursor
                cursor = f.tell()
                all_offset.append(f.tell())

                temp1 = struct.unpack('<I', f.read(4))[0]
                print(f"Read Offset {f.tell()-4}, Texture {j}, Mesh {k} Offset: {temp1}")
                f.read(12)

    #untuk mengurutkan offset setiap data yang sudah dibaca
    all_offset.sort()
    print(all_offset)
    print(len(all_offset))

    #menulis POF0 menggunakan offset yang sudah diurutkan
    f.seek(0, os.SEEK_END)
    for i in range(len(all_offset)-1):
        cursor = all_offset[i+1]
        temp = all_offset[i]
        out(f, cursor, temp)

    end_pof0=f.tell()
    f.seek(pof0_count_offset)
    pof0_lenght=end_pof0-start_pof0
    f.write(struct.pack('<I', pof0_lenght))

def join_object(b,t,selected_object):
    #variabel
    total_length = os.fstat(t.fileno()).st_size

    # Membaca pof0_offset
    t.seek(4)
    pof0_offset = struct.unpack('<I', t.read(4))[0]
    print(f"Offset POF0: {pof0_offset}")

    # Menghapus POF0
    t.seek(pof0_offset+8)
    length_to_truncate = total_length - t.tell()
    pof0_file = t.read(length_to_truncate)
    t.seek(-(length_to_truncate),1)
    t.truncate(t.tell())
    print(f"Menghapus POF0 {t.tell()}, sepanjang {length_to_truncate} byte.")

    #membaca mesh_count
    b.seek(24)
    base_mesh_count = struct.unpack('<I', b.read(4))[0]
    print(f"Read Offset {b.tell()-4}, Mesh Count: {base_mesh_count}")

    #membaca texture_count
    b.read(4)
    base_texture_count = struct.unpack('<I', b.read(4))[0]
    print(f"Read Offset {b.tell()-4}, Texture Count: {base_texture_count}")

    #membaca mesh_offset
    base_mesh_header_offset=b.tell()
    base_mesh_offset = struct.unpack('<I', b.read(4))[0]
    print(f"Read Offset {b.tell()-4}, Mesh Offset: {base_mesh_offset}")

    #menu pilih object
    b.seek(base_mesh_offset+8)
    for i in range(base_mesh_count):
        print(f"Read Object {i} Header at Offset {b.tell()}")
        mesh_header.append(b.read(64))
        pass
    b.seek(base_mesh_offset+8)
    print(f"Object List")
    for i in range(base_mesh_count):
        base_mesh_object_offset.append(b.tell())
        b.read(4)
        value = struct.unpack('<I', b.read(4))[0]
        base_mesh_texture_count.append(value)
        value = struct.unpack('<I', b.read(4))[0]
        base_mesh_vertice_header_1_offset.append(value)
        value = struct.unpack('<I', b.read(4))[0]
        base_mesh_texture_offset.append(value)
        b.read(8)
        value = struct.unpack('<I', b.read(4))[0]
        base_mesh_vertice_header_2_offset.append(value)
        b.read(12)
        value = struct.unpack('<I', b.read(4))[0]
        base_mesh_vertice_count.append(value)
        print(f"Object {i}, Offset {base_mesh_object_offset[i]}, Vertice Count {base_mesh_vertice_count[i]}")
        b.read(20)
    join_this_object(b,t,selected_object)

def join_this_object(b,t,object_pilihan):
    texture_block_offset_new=[]
    new_header=[]
    #copy mesh_vertice_header_1_offset ke paling bawah
    b.seek(base_mesh_vertice_header_1_offset[object_pilihan]+8)
    print(f"Mesh Header 1 Offset: {b.tell()}")
    value = b.read(48)
    t.seek(0, os.SEEK_END)
    new_vertex_header_1 = t.tell()
    print(f"Menulis data ke Offset {t.tell()}")
    t.write(value)

    #copy mesh_vertice_header_2_offset ke paling bawah
    b.seek(base_mesh_vertice_header_2_offset[object_pilihan]+8)
    print(f"Mesh Header 2 Offset: {b.tell()}")
    value = b.read(4)
    t.seek(0, os.SEEK_END)
    new_vertex_header_2 = t.tell()
    print(f"Menulis data ke Offset {t.tell()}")
    t.write(value)
    t.write(b'\x00' * 12)

    #update offset mesh vertice header
    update_header=t.tell()-8
    t.seek(-16,1)
    vertex_offset = struct.unpack('<I', t.read(4))[0]
    t.seek(-4,1)
    t.write(struct.pack('<I',update_header))
    print(f"Menulis ulang Vertex Header 2 Offset: {t.tell()-4}, Menjadi {update_header}")
    t.seek(-44,1)
    t.write(struct.pack('<I',update_header))
    print(f"Menulis ulang Vertex Header 1 Offset: {t.tell()-4}, Menjadi {update_header}")

    #copy Vertex
    b.seek(vertex_offset+8)
    print(f"Vertex Offset: {b.tell()}")
    vertex_lenght = 32+(44*base_mesh_vertice_count[object_pilihan])+(24*(base_mesh_vertice_count[object_pilihan]-1))
    value = b.read(vertex_lenght)
    t.seek(0, os.SEEK_END)
    print(f"Menulis data ke Offset {t.tell()} dengan panjang {vertex_lenght} byte")
    t.write(value)
    t.seek(0, os.SEEK_END)
    sisa = t.tell() % 16
    print(sisa)
    t.write(b'\x00' * sisa)

    #copy Texture
    b.seek(base_mesh_texture_offset[object_pilihan]+8)
    cursor=b.tell()
    mesh_texture_new = []
    mesh_texture_block_count =[]
    for i in range(base_mesh_texture_count[object_pilihan]):
        print(f"Texture {i} Offset: {b.tell()}")
        value = b.read(144)
        cursor=b.tell()
        t.seek(0, os.SEEK_END)
        mesh_texture_new.append(t.tell())
        print(f"Menulis data ke Offset {t.tell()}")
        t.write(value)
        t.seek(-12,1)
        value=struct.unpack('<I', t.read(4))[0]
        print(f"Block Count: {value}")
        mesh_texture_block_count.append(value)
        value=struct.unpack('<I', t.read(4))[0]
        mesh_block_offset.append(value)
        print(f"Block Offset: {value}")

    #copy block
    for i in range(base_mesh_texture_count[object_pilihan]):
        b.seek(mesh_block_offset[i]+8)
        block_isi=[]
        block_offset=[]
        block_offset_new=[]
        block_mesh=[]
        mesh_block_offset_new=[]
        for j in range(mesh_texture_block_count[i]):
            block_isi.append(b.read(16))
            b.seek(-4,1)
            value=struct.unpack('<I', b.read(4))[0]
            print(f"Read Offset {b.tell()-4}, Texture {i}, Block {j}, Block Offset: {value}")
            block_offset.append(value)
            pass
        t.seek(0, os.SEEK_END)
        texture_block_offset_new.append(t.tell())
        for j in range(mesh_texture_block_count[i]):
            value = t.tell()
            mesh_block_offset_new.append(value)
            t.write(block_isi[j])
            print(f"Write at {value}, Texture {i}, Block {j}")
            pass
        t.seek(0, os.SEEK_END)
        lenght=0
        j=0
        print(f"test: {mesh_texture_block_count[i]-1}")
        if mesh_texture_block_count[i]>1:
            for j in range(mesh_texture_block_count[i]-1):
                lenght = block_offset[j+1]-block_offset[j]
                b.seek(block_offset[j]+8)
                block_mesh.append(b.read(lenght))
                value = t.tell()
                block_offset_new.append(value)
                print(f"block offset new: {value}")
                t.write(block_mesh[j])
                print(f"Write at {value}, Texture {i}, block {j}, lenght {lenght}")
                pass
            value = t.tell()
            block_offset_new.append(value)
            b.seek(block_offset[j+1]+8)
            block_mesh.append(b.read(lenght))
            t.write(block_mesh[j+1])
            print(f"Write at {value}, Texture {i}, block {j+1}, lenght {lenght}")
        else:
            value = t.tell()
            block_offset_new.append(value)
            b.seek(block_offset[j]+8)
            block_mesh.append(b.read(lenght))
            t.write(block_mesh[j])
            print(f"Write at {value}, Texture {i}, block {j+1}, lenght {lenght}")
            pass

        #update Offset block
        for j in range(mesh_texture_block_count[i]):
            t.seek(mesh_block_offset_new[j]+12)
            print(f"Write at {t.tell()}, Texture {i}, Block {j}, New Block Offset")
            t.write(struct.pack('<I',block_offset_new[j]-8))
        pass

    #update offset texture block
    for i in range(base_mesh_texture_count[object_pilihan]):
        t.seek(mesh_texture_new[i])
        print(f"Write Texture {i} New Block Offset at {t.tell()}")
        t.read(136)
        t.write(struct.pack('<I',texture_block_offset_new[i]-8))
        texture_block_end=texture_block_offset_new[i]+(16*mesh_texture_block_count[i])
        t.write(struct.pack('<I',texture_block_end-8))
        pass
    t.seek(0, os.SEEK_END)
    cursor=t.tell()
    new_mesh_header_offset = t.tell()
    t.write(mesh_header[object_pilihan])
    t.seek(cursor)
    t.read(8)
    print(f"Write New Object Header at {t.tell()}, Vertex Header 1")
    t.write(struct.pack('<I',new_vertex_header_1-8))
    print(f"Write New Object Header at {t.tell()}, Texture Header")
    t.write(struct.pack('<I',mesh_texture_new[0]-8))
    t.read(8)
    print(f"Write New Object Header at {t.tell()}, Vertex Header 2")
    t.write(struct.pack('<I',new_vertex_header_2-8))
    t.seek(cursor)
    print(f"Write New Object {object_pilihan} Header to new_header")
    new_header.append(t.read(64))

    #copy original header mesh
    t.seek(24)
    target_mesh_count=struct.unpack('<I', t.read(4))[0]
    print(f"Target Mesh Count: {target_mesh_count}")
    t.seek(36)
    target_header_mesh_offset=struct.unpack('<I', t.read(4))[0]
    print(f"Target Mesh Offset: {target_header_mesh_offset}")
    t.seek(target_header_mesh_offset+8)
    target_mesh_header=[]
    for i in range(target_mesh_count):
        print(f"Read Target Mesh Header Object {i} at offset {t.tell()}")
        target_mesh_header.append(t.read(64))
        pass

    #paste
    t.seek(0, os.SEEK_END)
    for i in range(target_mesh_count):
        print(f"Write Target Mesh Header Object {i} at offset {t.tell()}")
        t.write(target_mesh_header[i])
        pass
    new_pof0_offset=t.tell()
    t.seek(24)
    print(f"Update Target Mesh Count at {t.tell()}")
    t.write(struct.pack('<I',target_mesh_count+1))
    t.seek(36)
    print(f"Update Target Header Mesh Offset at {t.tell()}")
    t.write(struct.pack('<I',new_mesh_header_offset-8))
    t.seek(4)
    print(f"Update Target POF0 Offset at {t.tell()}")
    t.write(struct.pack('<I',new_pof0_offset-8))
    t.read(4)
    print(f"Update Target POF0 Offset at {t.tell()}")
    t.write(struct.pack('<I',new_pof0_offset-8))

def reset_variables():
    global base_mesh_object_offset, base_mesh_texture_count, base_mesh_vertice_header_1_offset
    global base_mesh_texture_offset, base_mesh_vertice_header_2_offset, base_mesh_vertice_count
    global mesh_block_offset, mesh_header

    base_mesh_object_offset = []
    base_mesh_texture_count = []
    base_mesh_vertice_header_1_offset = []
    base_mesh_texture_offset = []
    base_mesh_vertice_header_2_offset = []
    base_mesh_vertice_count = []
    mesh_block_offset = []
    mesh_header = []

def main(base_file, target_file, selected_object):
    reset_variables()

    try:
        base_yobj = open(base_file, "rb")
    except IOError:
        print(f"Cannot open {base_file}")
        return 1

    try:
        target_yobj = open(target_file, "r+b")
    except IOError:
        print(f"Cannot open {target_file}")
        return 1

    join_object(base_yobj, target_yobj, selected_object)
    generate_pof0(target_yobj)  # Panggil fungsi generate_pof0 sesuai kebutuhan

    base_yobj.close()
    target_yobj.close()
    return 0

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Join Object YOBJ")

        # Mengatur agar jendela otomatis menyesuaikan ukurannya dengan konten
        self.root.resizable(False, False)

        # Bagian Browse untuk Model Dasar
        self.label_base = tk.Label(root, text="Base YOBJ File:")
        self.label_base.pack()

        self.entry_base = tk.Entry(root, width=80)
        self.entry_base.pack()

        self.button_base = tk.Button(root, text="Browse", command=self.browse_base)
        self.button_base.pack()

        # Daftar Objek
        self.listbox_objects = tk.Listbox(root, width=100, height=15)
        self.listbox_objects.pack()

        # Tombol Gabungkan Objek yang juga melakukan Browse untuk Target YOBJ
        self.button_join = tk.Button(root, text="Join Object to Target YOBJ", command=self.browse_and_join)
        self.button_join.pack()

        # Tombol Gabungkan Semua Objek
        self.button_join_all = tk.Button(root, text="Join All Object to Target YOBJ", command=self.browse_and_join_all)
        self.button_join_all.pack()

    def browse_base(self):
        filename = filedialog.askopenfilename(title="Pick Base YOBJ File", filetypes=[("YOBJ files", "*.yobj")])
        if filename:
            self.entry_base.delete(0, tk.END)
            self.entry_base.insert(0, filename)
            self.load_objects(filename)

    def load_objects(self, base_file):
        reset_variables()
        try:
            with open(base_file, "rb") as b:
                b.seek(24)  # Posisi untuk membaca mesh_count
                base_mesh_count = struct.unpack('<I', b.read(4))[0]
                b.seek(36)  # Posisi untuk membaca mesh_count
                base_mesh_offset = struct.unpack('<I', b.read(4))[0]

                b.seek(base_mesh_offset + 8)  # Posisi offset objek
                self.listbox_objects.delete(0, tk.END)  # Kosongkan listbox sebelumnya

                for i in range(base_mesh_count):
                    base_mesh_object_offset.append(b.tell())
                    b.read(4)
                    value = struct.unpack('<I', b.read(4))[0]
                    base_mesh_texture_count.append(value)
                    value = struct.unpack('<I', b.read(4))[0]
                    base_mesh_vertice_header_1_offset.append(value)
                    value = struct.unpack('<I', b.read(4))[0]
                    base_mesh_texture_offset.append(value)
                    b.read(8)
                    value = struct.unpack('<I', b.read(4))[0]
                    base_mesh_vertice_header_2_offset.append(value)
                    b.read(12)
                    value = struct.unpack('<I', b.read(4))[0]
                    base_mesh_vertice_count.append(value)
                    object_info = f"Object {i}, Offset: {base_mesh_object_offset[i]}, Vertice Count: {base_mesh_vertice_count[i]}"
                    self.listbox_objects.insert(tk.END, object_info)
                    b.read(20)

        except IOError:
            messagebox.showerror("Error", f"Cannot open {base_file}")

    def browse_and_join(self):
        # Meminta pengguna untuk memilih file target YOBJ sebelum menjalankan join object
        target_file = filedialog.askopenfilename(title="Pick Target YOBJ File", filetypes=[("YOBJ files", "*.yobj")])
        if target_file:
            base_file = self.entry_base.get()
            selected_index = self.listbox_objects.curselection()
            if selected_index:
                selected_object = selected_index[0]
                main(base_file, target_file, selected_object)
                messagebox.showinfo("Success", "Object Joined to target YOBJ!")
            else:
                messagebox.showwarning("Attention", "Pick single Object from list")

    def browse_and_join_all(self):
        # Meminta pengguna untuk memilih file target YOBJ sebelum menjalankan join semua objek
        target_file = filedialog.askopenfilename(title="Pick Target YOBJ File", filetypes=[("YOBJ files", "*.yobj")])
        if target_file:
            base_file = self.entry_base.get()
            base_mesh_count = len(self.listbox_objects.get(0, tk.END))

            for selected_object in range(base_mesh_count):
                reset_variables()  # Reset variabel setiap kali join object agar berjalan normal
                main(base_file, target_file, selected_object)

            messagebox.showinfo("Success", "All Object Joined to Target YOBJ!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()