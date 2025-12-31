// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

    // Initialize R2 = 0
    @R2
    M=0
    
    // Load R0 into D (counter for loop)
    @R0
    D=M
    
    // If R0 <= 0, skip to END
    @END
    D;JLE
    
    // Store R0 value in a temp variable for loop counter
    @R0
    D=M
    @counter
    M=D
    
(LOOP)
    // Check if counter <= 0
    @counter
    D=M
    @END
    D;JLE
    
    // Add R1 to R2
    @R1
    D=M
    @R2
    M=M+D
    
    // Decrement counter
    @counter
    M=M-1
    
    // Jump back to LOOP
    @LOOP
    0;JMP
    
(END)
    @END
    0;JMP
