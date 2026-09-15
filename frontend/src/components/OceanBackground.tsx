"use client";

import { useEffect, useRef } from "react";

type OceanParticle = {
  x: number;
  y: number;
  radius: number;
  speed: number;
  drift: number;
  phase: number;
  alpha: number;
};

type OceanFish = {
  x: number;
  y: number;
  speed: number;
  size: number;
  direction: 1 | -1;
  phase: number;
  glow: number;
  depth: number;
};

function createParticle(
  width: number,
  height: number,
): OceanParticle {
  return {
    x:
      Math.random() *
      width,

    y:
      Math.random() *
      height,

    radius:
      Math.random() *
        1.8 +
      0.35,

    speed:
      Math.random() *
        0.18 +
      0.035,

    drift:
      Math.random() *
        0.45 +
      0.1,

    phase:
      Math.random() *
      Math.PI *
      2,

    alpha:
      Math.random() *
        0.55 +
      0.18,
  };
}

function createFish(
  width: number,
  height: number,
): OceanFish {

  const direction =
    Math.random() >
    0.5
      ? 1
      : -1;

  return {
    x:
      Math.random() *
        width +
      (
        direction === 1
          ? -width *
            0.25
          : width *
            0.25
      ),

    y:
      Math.random() *
        height *
        0.82 +
      height *
        0.08,

    speed:
      Math.random() *
        0.42 +
      0.12,

    size:
      Math.random() *
        11 +
      5,

    direction,

    phase:
      Math.random() *
      Math.PI *
      2,

    glow:
      Math.random() *
        0.45 +
      0.55,

    depth:
      Math.random(),
  };
}

function drawFish(
  ctx: CanvasRenderingContext2D,
  fish: OceanFish,
  time: number,
) {

  const direction =
    fish.direction;

  const x =
    fish.x;

  const y =
    fish.y +
    Math.sin(
      time *
        0.00065 +
        fish.phase,
    ) *
      7;

  const size =
    fish.size;

  const opacity =
    0.2 +
    fish.depth *
      0.55;

  const glow =
    6 +
    fish.glow *
      16;

  ctx.save();

  ctx.translate(
    x,
    y,
  );

  if (
    direction ===
    -1
  ) {
    ctx.scale(
      -1,
      1,
    );
  }

  ctx.globalAlpha =
    opacity;

  // ----------------------------------------------------------
  // Bioluminescent aura
  // ----------------------------------------------------------

  ctx.shadowColor =
    `rgba(
      80,
      230,
      255,
      ${0.45 * fish.glow}
    )`;

  ctx.shadowBlur =
    glow;

  // ----------------------------------------------------------
  // Main body
  // ----------------------------------------------------------

  const bodyGradient =
    ctx.createLinearGradient(
      -size,
      0,
      size,
      0,
    );

  bodyGradient.addColorStop(
    0,
    "rgba(100,245,255,0.08)",
  );

  bodyGradient.addColorStop(
    0.45,
    "rgba(80,220,255,0.42)",
  );

  bodyGradient.addColorStop(
    1,
    "rgba(30,150,210,0.16)",
  );

  ctx.fillStyle =
    bodyGradient;

  ctx.beginPath();

  ctx.ellipse(
    0,
    0,
    size,
    size *
      0.42,
    0,
    0,
    Math.PI * 2,
  );

  ctx.fill();

  // ----------------------------------------------------------
  // Tail
  // ----------------------------------------------------------

  ctx.beginPath();

  ctx.moveTo(
    -size *
      0.68,
    0,
  );

  ctx.lineTo(
    -size *
      1.35,
    -size *
      0.56,
  );

  ctx.lineTo(
    -size *
      1.18,
    0,
  );

  ctx.lineTo(
    -size *
      1.35,
    size *
      0.56,
  );

  ctx.closePath();

  ctx.fillStyle =
    "rgba(100,235,255,0.3)";

  ctx.fill();

  // ----------------------------------------------------------
  // Dorsal fin
  // ----------------------------------------------------------

  ctx.beginPath();

  ctx.moveTo(
    -size *
      0.05,
    -size *
      0.3,
  );

  ctx.lineTo(
    size *
      0.18,
    -size *
      0.92,
  );

  ctx.lineTo(
    size *
      0.42,
    -size *
      0.22,
  );

  ctx.closePath();

  ctx.fillStyle =
    "rgba(130,245,255,0.22)";

  ctx.fill();

  // ----------------------------------------------------------
  // Bioluminescent dots
  // ----------------------------------------------------------

  ctx.shadowColor =
    "rgba(120,255,255,0.95)";

  ctx.shadowBlur =
    10;

  ctx.fillStyle =
    "rgba(170,255,255,0.9)";

  ctx.beginPath();

  ctx.arc(
    size *
      0.38,
    -size *
      0.03,
    Math.max(
      0.8,
      size *
        0.075,
    ),
    0,
    Math.PI * 2,
  );

  ctx.fill();

  ctx.beginPath();

  ctx.arc(
    -size *
      0.05,
    size *
      0.09,
    Math.max(
      0.55,
      size *
        0.055,
    ),
    0,
    Math.PI * 2,
  );

  ctx.fill();

  ctx.restore();
}

export default function OceanBackground() {

  const canvasRef =
    useRef<
      HTMLCanvasElement |
      null
    >(null);

  useEffect(() => {

    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext(
        "2d",
        {
          alpha: true,
        },
      );

    if (!ctx) {
      return;
    }

    let width =
      0;

    let height =
      0;

    let dpr =
      1;

    let animationFrame =
      0;

    let destroyed =
      false;

    const reducedMotion =
      window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches;

    const particleCount =
      reducedMotion
        ? 35
        : 115;

    const fishCount =
      reducedMotion
        ? 6
        : 24;

    let particles:
      OceanParticle[] =
        [];

    let fish:
      OceanFish[] =
        [];

    // --------------------------------------------------------
    // Resize
    // --------------------------------------------------------

    const resize =
      () => {

        width =
          window.innerWidth;

        height =
          window.innerHeight;

        dpr =
          Math.min(
            window.devicePixelRatio ||
              1,
            2,
          );

        canvas.width =
          Math.floor(
            width *
              dpr,
          );

        canvas.height =
          Math.floor(
            height *
              dpr,
          );

        canvas.style.width =
          `${width}px`;

        canvas.style.height =
          `${height}px`;

        ctx.setTransform(
          dpr,
          0,
          0,
          dpr,
          0,
          0,
        );

        particles =
          Array.from(
            {
              length:
                particleCount,
            },
            () =>
              createParticle(
                width,
                height,
              ),
          );

        fish =
          Array.from(
            {
              length:
                fishCount,
            },
            () =>
              createFish(
                width,
                height,
              ),
          );
      };

    // --------------------------------------------------------
    // Draw
    // --------------------------------------------------------

    const drawOcean =
      (time: number) => {

        if (destroyed) {
          return;
        }

        ctx.clearRect(
          0,
          0,
          width,
          height,
        );

        // ----------------------------------------------------
        // Deep ocean base
        // ----------------------------------------------------

        const base =
          ctx.createLinearGradient(
            0,
            0,
            0,
            height,
          );

        base.addColorStop(
          0,
          "#07151d",
        );

        base.addColorStop(
          0.42,
          "#04141e",
        );

        base.addColorStop(
          1,
          "#01070d",
        );

        ctx.fillStyle =
          base;

        ctx.fillRect(
          0,
          0,
          width,
          height,
        );

        // ----------------------------------------------------
        // Moving underwater light field
        // ----------------------------------------------------

        const glowOneX =
          width *
          (
            0.5 +
            Math.sin(
              time *
                0.00008,
            ) *
              0.18
          );

        const glowOneY =
          height *
          (
            0.22 +
            Math.sin(
              time *
                0.00011 +
                1.5,
            ) *
              0.08
          );

        const lightOne =
          ctx.createRadialGradient(
            glowOneX,
            glowOneY,
            0,
            glowOneX,
            glowOneY,
            width *
              0.55,
          );

        lightOne.addColorStop(
          0,
          "rgba(50,190,220,0.11)",
        );

        lightOne.addColorStop(
          0.45,
          "rgba(20,110,145,0.045)",
        );

        lightOne.addColorStop(
          1,
          "rgba(0,0,0,0)",
        );

        ctx.fillStyle =
          lightOne;

        ctx.fillRect(
          0,
          0,
          width,
          height,
        );

        // ----------------------------------------------------
        // Water-current lines
        // ----------------------------------------------------

        ctx.save();

        ctx.globalAlpha =
          reducedMotion
            ? 0.05
            : 0.09;

        ctx.lineWidth =
          1;

        for (
          let band = 0;
          band < 10;
          band++
        ) {

          const yBase =
            height *
            (
              0.06 +
              band *
                0.105
            );

          ctx.beginPath();

          for (
            let x = -40;
            x <=
              width + 40;
            x += 24
          ) {

            const wave =
              Math.sin(
                x *
                  0.009 +
                  time *
                    0.00022 +
                  band,
              ) *
              12;

            const cross =
              Math.sin(
                x *
                  0.021 -
                  time *
                    0.00013,
              ) *
              5;

            const y =
              yBase +
              wave +
              cross;

            if (
              x ===
              -40
            ) {

              ctx.moveTo(
                x,
                y,
              );

            } else {

              ctx.lineTo(
                x,
                y,
              );
            }
          }

          ctx.strokeStyle =
            "rgba(82,207,226,0.30)";

          ctx.stroke();
        }

        ctx.restore();

        // ----------------------------------------------------
        // Floating particles
        // ----------------------------------------------------

        for (
          const particle of
            particles
        ) {

          particle.y -=
            particle.speed;

          particle.x +=
            Math.sin(
              time *
                0.00035 +
                particle.phase,
            ) *
            particle.drift *
            0.08;

          if (
            particle.y <
            -10
          ) {

            particle.y =
              height +
              10;

            particle.x =
              Math.random() *
              width;
          }

          if (
            particle.x <
            -10
          ) {
            particle.x =
              width +
              10;
          }

          if (
            particle.x >
            width +
              10
          ) {
            particle.x =
              -10;
          }

          const twinkle =
            0.7 +
            Math.sin(
              time *
                0.001 +
                particle.phase,
            ) *
              0.3;

          ctx.beginPath();

          ctx.arc(
            particle.x,
            particle.y,
            particle.radius,
            0,
            Math.PI * 2,
          );

          ctx.fillStyle =
            `rgba(
              110,
              235,
              255,
              ${
                particle.alpha *
                twinkle
              }
            )`;

          ctx.shadowColor =
            "rgba(80,230,255,0.55)";

          ctx.shadowBlur =
            7;

          ctx.fill();
        }

        ctx.shadowBlur =
          0;

        // ----------------------------------------------------
        // Fish
        // ----------------------------------------------------

        for (
          const swimmer of
            fish
        ) {

          swimmer.x +=
            swimmer.speed *
            swimmer.direction;

          // Wrap horizontally.
          if (
            swimmer.direction ===
              1 &&
            swimmer.x >
              width +
                width *
                  0.18
          ) {

            swimmer.x =
              -width *
              0.18;
          }

          if (
            swimmer.direction ===
              -1 &&
            swimmer.x <
              -width *
                0.18
          ) {

            swimmer.x =
              width +
              width *
                0.18;
          }

          // Slight vertical movement.
          swimmer.y +=
            Math.sin(
              time *
                0.0004 +
                swimmer.phase,
            ) *
            0.06;

          drawFish(
            ctx,
            swimmer,
            time,
          );
        }

        // ----------------------------------------------------
        // Central readability
        // ----------------------------------------------------

        const vignette =
          ctx.createRadialGradient(
            width *
              0.5,
            height *
              0.46,
            height *
              0.12,
            width *
              0.5,
            height *
              0.5,
            Math.max(
              width,
              height,
            ) *
              0.82,
          );

        vignette.addColorStop(
          0,
          "rgba(0,0,0,0)",
        );

        vignette.addColorStop(
          0.66,
          "rgba(0,0,0,0.16)",
        );

        vignette.addColorStop(
          1,
          "rgba(0,0,0,0.68)",
        );

        ctx.fillStyle =
          vignette;

        ctx.fillRect(
          0,
          0,
          width,
          height,
        );

        // ----------------------------------------------------
        // Top haze
        // ----------------------------------------------------

        const haze =
          ctx.createLinearGradient(
            0,
            0,
            0,
            height *
              0.36,
          );

        haze.addColorStop(
          0,
          "rgba(72,220,240,0.08)",
        );

        haze.addColorStop(
          1,
          "rgba(0,0,0,0)",
        );

        ctx.fillStyle =
          haze;

        ctx.fillRect(
          0,
          0,
          width,
          height *
            0.36,
        );
      };

    const tick =
      (time: number) => {

        if (destroyed) {
          return;
        }

        drawOcean(
          time,
        );

        if (
          document.visibilityState !==
          "hidden"
        ) {

          animationFrame =
            window.requestAnimationFrame(
              tick,
            );
        }
      };

    const handleVisibility =
      () => {

        if (
          document.visibilityState ===
          "visible"
        ) {

          animationFrame =
            window.requestAnimationFrame(
              tick,
            );
        }
      };

    resize();

    window.addEventListener(
      "resize",
      resize,
      {
        passive: true,
      },
    );

    document.addEventListener(
      "visibilitychange",
      handleVisibility,
    );

    animationFrame =
      window.requestAnimationFrame(
        tick,
      );

    return () => {

      destroyed =
        true;

      window.removeEventListener(
        "resize",
        resize,
      );

      document.removeEventListener(
        "visibilitychange",
        handleVisibility,
      );

      window.cancelAnimationFrame(
        animationFrame,
      );
    };

  }, []);

  return (
    <div
      aria-hidden="true"
      className="
        pointer-events-none
        fixed
        inset-0
        z-0
        overflow-hidden
      "
    >

      <canvas
        ref={canvasRef}
        className="
          absolute
          inset-0
          h-full
          w-full
        "
      />

    </div>
  );
}
