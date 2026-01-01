// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

(LOOP)
    // Read keyboard input
    @24576  // KBD register
    D=M     // D = keyboard value (0 if no key, non-0 if key pressed)
    
    // Initialize screen pointer and counter
    @16384  // Screen base address
    D=A
    @addr
    M=D     // addr = 16384
    
    @8192   // Number of screen words (16384 pixels / 16 pixels per word)
    D=A
    @n
    M=D     // n = 8192
    
    // Check keyboard state and set fill value
    @24576
    D=M
    @FILL_BLACK
    D;JNE   // If KBD != 0, jump to FILL_BLACK
    
    // Fill white (0)
    @color
    M=0     // color = 0 (white)
    @FILL
    0;JMP
    
(FILL_BLACK)
    @color
    M=-1    // color = -1 (black, all bits set)
    
(FILL)
    @n
    D=M
    @LOOP
    D;JEQ   // If n == 0, return to LOOP (refresh keyboard)
    
    // Write color to screen
    @color
    D=M
    @addr
    A=M
    M=D     // Memory[addr] = color
    
    // Move to next word
    @addr
    M=M+1
    
    // Decrement counter
    @n
    M=M-1
    
    @FILL
    0;JMP   // Continue filling
