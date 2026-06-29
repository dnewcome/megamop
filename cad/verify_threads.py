"""verify_threads.py — assert the male/female thread pairs actually MESH.

py cad/verify_threads.py   (exits non-zero if any pair won't screw together)

The renders only OVERLAY thread ribs; they don't prove screw-ability. This checks the
radial geometry that determines whether same-pitch/same-hand threads interlock:
  engagement = male_crest_R - female_crest_R   (flank overlap; must be clearly > 0)
  plus tip clearances so neither crest bottoms out in the other's groove.
"""
import sys
import machine_params as M

MIN_ENGAGE = 0.4   # mm radial flank overlap we require
MIN_TIPCLR = 0.15  # mm crest-tip clearance we require


def check(name, male_crest, male_root, fem_crest, fem_root, pitch_m, pitch_f,
          starts_m, starts_f):
    eng = male_crest - fem_crest
    cl_male = fem_root - male_crest
    cl_fem = fem_crest - male_root
    ok = (eng >= MIN_ENGAGE and cl_male >= MIN_TIPCLR and cl_fem >= MIN_TIPCLR
          and abs(pitch_m - pitch_f) < 1e-6 and starts_m == starts_f)
    print(f"[{'OK ' if ok else 'FAIL'}] {name}: engage={eng:+.2f} "
          f"tipclr(m={cl_male:+.2f},f={cl_fem:+.2f}) "
          f"pitch {pitch_m}/{pitch_f} starts {starts_m}/{starts_f}")
    return ok


def main():
    bmaj = M.BOTTLE_THREAD_MAJOR_D / 2
    results = [
        check("cup<->collar/dome", M.CUP_THREAD_CREST_R, M.CUP_THREAD_ROOT_R,
              M.COLLAR_CREST_R, M.COLLAR_BORE_R,
              M.CUP_THREAD_PITCH, M.CUP_THREAD_PITCH,
              M.CUP_THREAD_STARTS, M.CUP_THREAD_STARTS),
        check("bottle<->skirt", bmaj, bmaj - M.BOTTLE_THREAD_DEPTH,
              M.SKIRT_CREST_R, M.SKIRT_BORE_R,
              M.BOTTLE_THREAD_PITCH, M.BOTTLE_THREAD_PITCH,
              M.BOTTLE_THREAD_STARTS, M.BOTTLE_THREAD_STARTS),
    ]
    if not all(results):
        sys.exit("THREAD MESH CHECK FAILED")
    print("all thread pairs mesh.")


if __name__ == "__main__":
    main()
