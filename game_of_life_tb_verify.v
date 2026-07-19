`timescale 1ns / 1ps

module game_of_life_pipeline_tb;

    parameter GRID_SIZE  = 32;
    parameter CLK_PERIOD = 10;

    reg clk;
    reg rst;
    reg load;
    reg [GRID_SIZE*GRID_SIZE-1:0] load_data;
    wire [GRID_SIZE*GRID_SIZE-1:0] grid_out;

    integer in_file, out_file, ready_file;
    integer status;
    
    game_of_life #(
        .GRID_SIZE(GRID_SIZE)
    ) dut (
        .clk(clk),
        .rst(rst),
        .load(load),
        .load_data(load_data),
        .grid_out(grid_out)
    );

    initial clk = 1'b0;
    always #(CLK_PERIOD/2) clk = ~clk;

    initial begin
        rst  = 1'b1;
        load = 1'b0;
        load_data = {GRID_SIZE*GRID_SIZE{1'b0}};
        #(CLK_PERIOD * 2);
        rst  = 1'b0;
        
        $display("[Verilog] Pipeline engine active. Awaiting Python input...");

        forever begin
            in_file = $fopen("input.ready", "r");
            while (in_file == 0) begin
                #100; 
                in_file = $fopen("input.ready", "r");
            end
            $fclose(in_file);
            
            $system("rm -f input.ready"); 

            in_file = $fopen("input.txt", "r");
            if (in_file != 0) begin
                status = $fscanf(in_file, "%h\n", load_data);
                $fclose(in_file);
            end

            load <= 1'b1;
            @(posedge clk);
            load <= 1'b0;

            @(posedge clk);
            #1; 
            out_file = $fopen("output.txt", "w");
            if (out_file != 0) begin
                $fwrite(out_file, "%h\n", grid_out);
                $fclose(out_file);
            end

            ready_file = $fopen("output.ready", "w");
            if (ready_file != 0) begin
                $fwrite(ready_file, "1");
                $fclose(ready_file);
            end
        end
    end

endmodule
