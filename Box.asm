// Box.asm (K = 5)
// Box starts at row 5, is 20 rows tall and 2 words (32 pixels) wide.
// Black while any key is pressed, white when released.
// Start address = SCREEN + 32*5 = 16384 + 160 = 16544

(LOOP)
    // Check whether any key is pressed
    @KBD
    D=M
    @BLACK
    D;JNE

    // If no key is pressed, set color to white
    @color
    M=0
    @DRAW
    0;JMP

(BLACK)
    // If a key is pressed, set color to black
    @color
    M=-1

(DRAW)
    // Set total number of rows to 20
    @20
    D=A
    @rows
    M=D

    // Set starting screen address to row 5
    @16544
    D=A
    @addr
    M=D

(ROW)
    // Each row contains 2 words (32 pixels)
    @2
    D=A
    @cols
    M=D

    // Store current row address in p
    @addr
    D=M
    @p
    M=D

(COL)
    // Get current color
    @color
    D=M

    // Draw pixels at current screen address
    @p
    A=M
    M=D

    // Move to next screen word
    @p
    M=M+1

    // Decrease column counter
    @cols
    MD=M-1
    @COL
    D;JGT

    // Move to the next screen row (32 words)
    @32
    D=A
    @addr
    M=D+M

    // Decrease row counter
    @rows
    MD=M-1
    @ROW
    D;JGT

    // Continuously check keyboard input
    @LOOP
    0;JMP