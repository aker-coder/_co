// push constant 111
@111
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 333
@333
D=A
@SP
A=M
M=D
@SP
M=M+1
// push constant 888
@888
D=A
@SP
A=M
M=D
@SP
M=M+1
// pop static 8
// pop static 3
// pop static 1
// push static 3
// push static 1
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// push static 8
// add
@SP
AM=M-1
D=M
A=A-1
M=M+D
