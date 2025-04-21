#=========================================================================
# SingleCoreSysFL_test.py
#=========================================================================
# We apply select tests from lab2 to the single core system.

import pytest

from pymtl3 import *

from lab4_sys.test.harness import asm_test
from lab4_sys.test.harness import run_score_test as run_test

from lab4_sys.SingleCoreSysFL import SingleCoreSysFL

from lab2_proc.test import inst_csr
from lab2_proc.test import inst_add
from lab2_proc.test import inst_mul
from lab2_proc.test import inst_addi
from lab2_proc.test import inst_lw
from lab2_proc.test import inst_sw
from lab2_proc.test import inst_bne
from lab2_proc.test import inst_jal
from lab2_proc.test import inst_jalr
from lab2_proc.test import inst_lui

#-------------------------------------------------------------------------
# Tests
#-------------------------------------------------------------------------

@pytest.mark.usefixtures("cmdline_opts")
class Tests:

  @classmethod
  def setup_class( cls ):
    cls.SysType = SingleCoreSysFL

  #-----------------------------------------------------------------------
  # csr
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_csr.gen_basic_test      ),
    asm_test( inst_csr.gen_bypass_test     ),
    asm_test( inst_csr.gen_value_test      ),
    asm_test( inst_csr.gen_random_test     ),
    asm_test( inst_csr.gen_core_stats_test ),
  ])
  def test_csr( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_csr_delays( s ):
    run_test( s.SysType, inst_csr.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # add
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_add.gen_basic_test     ),
    asm_test( inst_add.gen_dest_dep_test  ),
    asm_test( inst_add.gen_src0_dep_test  ),
    asm_test( inst_add.gen_src1_dep_test  ),
    asm_test( inst_add.gen_srcs_dep_test  ),
    asm_test( inst_add.gen_srcs_dest_test ),
    asm_test( inst_add.gen_value_test     ),
    asm_test( inst_add.gen_random_test    ),
  ])
  def test_add( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_add_delays( s ):
    run_test( s.SysType, inst_add.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # mul
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_mul.gen_basic_test     ),
    asm_test( inst_mul.gen_dest_dep_test  ),
    asm_test( inst_mul.gen_src0_dep_test  ),
    asm_test( inst_mul.gen_src1_dep_test  ),
    asm_test( inst_mul.gen_srcs_dep_test  ),
    asm_test( inst_mul.gen_srcs_dest_test ),
    asm_test( inst_mul.gen_value_test     ),
    asm_test( inst_mul.gen_random_test    ),
  ])
  def test_mul( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_mul_delays( s ):
    run_test( s.SysType, inst_mul.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # addi
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_addi.gen_basic_test     ) ,
    asm_test( inst_addi.gen_dest_dep_test    ) ,
    asm_test( inst_addi.gen_src_dep_test     ) ,
    asm_test( inst_addi.gen_srcs_dest_test   ) ,
    asm_test( inst_addi.gen_value_test       ) ,
    asm_test( inst_addi.gen_random_test      ) ,
  ])

  def test_addi( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )
  
  def test_addi_delays( s ):
    run_test( s.SysType, inst_addi.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # lw
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lw.gen_basic_test     ) ,
    asm_test( inst_lw.gen_dest_dep_test  ) ,
    asm_test( inst_lw.gen_base_dep_test  ) ,
    asm_test( inst_lw.gen_srcs_dest_test ) ,
    asm_test( inst_lw.gen_addr_test      ) ,
    asm_test( inst_lw.gen_random_test    ) ,
  ])
  def test_lw( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_lw_delays( s ):
    run_test( s.SysType, inst_lw.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # sw
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_sw.gen_basic_test     ),
    asm_test( inst_sw.gen_dest_dep_test  ),
    asm_test( inst_sw.dep_test           ),
    asm_test( inst_sw.dep_test_2         ),
    asm_test( inst_sw.gen_addr_test      ),
  ])

  def test_sw( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # bne
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_bne.gen_basic_test             ),
    asm_test( inst_bne.gen_src0_dep_taken_test    ),
    asm_test( inst_bne.gen_src0_dep_nottaken_test ),
    asm_test( inst_bne.gen_src1_dep_taken_test    ),
    asm_test( inst_bne.gen_src1_dep_nottaken_test ),
    asm_test( inst_bne.gen_srcs_dep_taken_test    ),
    asm_test( inst_bne.gen_srcs_dep_nottaken_test ),
    asm_test( inst_bne.gen_src0_eq_src1_test      ),
    asm_test( inst_bne.gen_value_test             ),
    asm_test( inst_bne.gen_back_to_back_test      ),
    asm_test( inst_bne.gen_random_test            ),
  ])
  def test_bne( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_bne_delays( s ):
    run_test( s.SysType, inst_bne.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )

  #-----------------------------------------------------------------------
  # jal
  #-----------------------------------------------------------------------

  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jal.gen_basic_test        ) ,
  ])

  def test_jal( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  #------------------------------------------------------------------------
  # jalr
  #------------------------------------------------------------------------
  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_jalr.gen_basic_test    ),
  ])

  def test_jalr( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  #------------------------------------------------------------------------
  # lui
  #------------------------------------------------------------------------
  @pytest.mark.parametrize( "name,test", [
    asm_test( inst_lui.gen_basic_test    ) ,
    asm_test( inst_lui.gen_dest_dep_test  ) ,
    asm_test( inst_lui.gen_value_test     ) ,
    asm_test( inst_lui.gen_random_test    ) ,
  ])

  def test_lui( s, name, test ):
    run_test( s.SysType, test, cmdline_opts=s.__class__.cmdline_opts )

  def test_lui_delays( s ):
    run_test( s.SysType, inst_lui.gen_random_test, delays=True,
              cmdline_opts=s.__class__.cmdline_opts )
