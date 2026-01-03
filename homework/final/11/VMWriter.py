class VMWriter:
    def __init__(self, output_file):
        self.output_file = output_file

    def write_push(self, segment, index):
        # segment: CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP
        # 注意: Python 的寫法要轉成 VM 的小寫關鍵字，例如 'CONST' -> 'constant'
        seg_map = {'CONST': 'constant', 'ARG': 'argument', 'LOCAL': 'local',
                   'STATIC': 'static', 'THIS': 'this', 'THAT': 'that', 
                   'POINTER': 'pointer', 'TEMP': 'temp'}
        self.output_file.write(f"push {seg_map.get(segment, segment)} {index}\n")

    def write_pop(self, segment, index):
        seg_map = {'CONST': 'constant', 'ARG': 'argument', 'LOCAL': 'local',
                   'STATIC': 'static', 'THIS': 'this', 'THAT': 'that', 
                   'POINTER': 'pointer', 'TEMP': 'temp'}
        self.output_file.write(f"pop {seg_map.get(segment, segment)} {index}\n")

    def write_arithmetic(self, command):
        # command: ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT
        self.output_file.write(f"{command.lower()}\n")

    def write_label(self, label):
        self.output_file.write(f"label {label}\n")

    def write_goto(self, label):
        self.output_file.write(f"goto {label}\n")

    def write_if(self, label):
        self.output_file.write(f"if-goto {label}\n")

    def write_call(self, name, n_args):
        self.output_file.write(f"call {name} {n_args}\n")

    def write_function(self, name, n_locals):
        self.output_file.write(f"function {name} {n_locals}\n")

    def write_return(self):
        self.output_file.write("return\n")