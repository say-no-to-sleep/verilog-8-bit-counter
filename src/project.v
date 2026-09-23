/*
 * Copyright (c) 2026 Eugene Zhao
 * SPDX-License-Identifier: Apache-2.0
 */

// Safety settings
`default_nettype none

module tt_um_counter (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire load = ui_in[0];
  wire out_en = ui_in[1];
  wire count_en = ui_in[2];

  // Register
  reg [7:0] count;

  // Clock go from 0 to 1
  // Reset go from 1 to 0
  always@(posedge clk or negedge rst_n) begin
    
    if(!rst_n) begin
      count <= 8'b00000000;
    end else if (load) begin
      count <= uio_in;
    end else if (count_en) begin
      count <= count + 8'b00000001;
    end

  end

  // All output pins must be assigned. If not used, assign to 0.
  // uo_out shows the count
  assign uo_out  = count;  // Example: ou_out is the sum of ui_in and uio_in
  // Also the count
  assign uio_out = count;
  // controls tri-state
  assign uio_oe  = out_en == 1 ? 8'hFF : 8'h00;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, ui_in[7:3], 1'b0};

endmodule
