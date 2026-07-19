`timescale 1ns / 1ps

module game_of_life #(
    parameter GRID_SIZE = 32
)(
    input  wire                             clk,
    input  wire                             rst,
    input  wire                             load,
    input  wire [(GRID_SIZE*GRID_SIZE)-1:0] load_data,
    output reg  [(GRID_SIZE*GRID_SIZE)-1:0] grid_out
);

    reg grid[0:GRID_SIZE-1][0:GRID_SIZE-1];
    
    integer r, c;
    integer nb_r, nb_c;
    integer live_neighbors;

    always @(posedge clk) begin
        if (rst) begin
            for (r = 0; r < GRID_SIZE; r = r + 1) begin
                for (c = 0; c < GRID_SIZE; c = c + 1) begin
                    grid[r][c] <= 1'b0;
                end
            end
        end 
        else if (load) begin
            for (r = 0; r < GRID_SIZE; r = r + 1) begin
                for (c = 0; c < GRID_SIZE; c = c + 1) begin
                    grid[r][c] <= load_data[r * GRID_SIZE + c];
                end
            end
        end 
        else begin
            for (r = 0; r < GRID_SIZE; r = r + 1) begin
                for (c = 0; c < GRID_SIZE; c = c + 1) begin
                    
                    live_neighbors = 0;
                    for (nb_r = -1; nb_r <= 1; nb_r = nb_r + 1) begin
                        for (nb_c = -1; nb_c <= 1; nb_c = nb_c + 1) begin
                            if (!(nb_r == 0 && nb_c == 0)) begin
                                live_neighbors = live_neighbors + 
                                    grid[(r + nb_r + GRID_SIZE) % GRID_SIZE][(c + nb_c + GRID_SIZE) % GRID_SIZE];
                            end
                        end
                    end

                    if (grid[r][c] == 1'b1) begin
                        if (live_neighbors == 2 || live_neighbors == 3)
                            grid[r][c] <= 1'b1;
                        else
                            grid[r][c] <= 1'b0;
                    end 
                    else begin
                        if (live_neighbors == 3)
                            grid[r][c] <= 1'b1;
                        else
                            grid[r][c] <= 1'b0;
                    end

                end
            end
        end
    end

    always @(*) begin
        for (r = 0; r < GRID_SIZE; r = r + 1) begin
            for (c = 0; c < GRID_SIZE; c = c + 1) begin
                grid_out[r * GRID_SIZE + c] = grid[r][c];
            end
        end
    end

endmodule



module game_of_life_synth_wrapper (
    input  wire clk,
    input  wire rst,
    input  wire load,
    input  wire serial_in,
    output reg  serial_out
);

    parameter GRID_SIZE = 32;
    
    reg [GRID_SIZE*GRID_SIZE-1:0] shift_reg_in;
    wire [GRID_SIZE*GRID_SIZE-1:0] grid_out;

    always @(posedge clk) begin
        if (rst)
            shift_reg_in <= 0;
        else
            shift_reg_in <= {shift_reg_in[GRID_SIZE*GRID_SIZE-2:0], serial_in};
    end

    game_of_life #(
        .GRID_SIZE(GRID_SIZE)
    ) core_engine (
        .clk(clk),
        .rst(rst),
        .load(load),
        .load_data(shift_reg_in),
        .grid_out(grid_out)
    );

    always @(posedge clk) begin
        serial_out <= ^grid_out; 
    end

endmodule
