"use client";

import { useEffect, useRef } from "react";

type Fish = {
  x: number;
  y: number;
  speed: number;
  size: number;
  direction: 1 | -1;
  phase: number;
  depth: number;
  color: string;
  accent: string;
};

type Particle = {
  x: number;
  y: number;
  radius: number;
  speed: number;
  phase: number;
  alpha: number;
};

const FISH_COLORS = [
  {
    color: "rgba(80,255,240,0.90)",
    accent: "rgba(0,180,255,0.70)",
  },
  {
    color: "rgba(255,100,225,0.90)",
    accent: "rgba(165,70,255,0.72)",
  },
  {
    color: "rgba(170,255,95,0.88)",
    accent: "rgba(30,210,120,0.68)",
  },
  {
    color: "rgba(255,230,95,0.90)",
    accent: "rgba(255,145,40,0.70)",
  },
  {
    color: "rgba(255,115,100,0.88)",
    accent: "rgba(255,50,125,0.70)",
  },
  {
    color: "rgba(200,145,255,0.88)",
    accent: "rgba(100,75,255,0.70)",
  },
  {
    color: "rgba(110,235,255,0.90)",
    accent: "rgba(65,125,255,0.70)",
  },
];

function makeFish(
  width: number,
  height: number,
): Fish {

  const direction =
    Math.random() > 0.5
      ? 1
      : -1;

  const palette =
    FISH_COLORS[
      Math.floor(
        Math.random() *
          FISH_COLORS.length,
      )
    ];

  return {
    x:
      direction === 1
        ? -Math.random() *
            width *
            0.3
        : width +
            Math.random() *
              width *
              0.3,

    y:
      Math.random() *
        height *
        0.9 +
      height *
        0.05,

    speed:
      0.015 +
      Math.random() *
        0.045,

    size:
      5 +
      Math.random() *
        12,

    direction,

    phase:
      Math.random() *
      Math.PI *
      2,

    depth:
      0.25 +
      Math.random() *
        0.75,

    color:
      palette.color,

    accent:
      palette.accent,
  };
}

function makeParticle(
  width: number,
  height: number,
): Particle {

  return {
    x:
      Math.random() *
      width,

    y:
      Math.random() *
      height,

    radius:
      0.4 +
      Math.random() *
        1.5,

    speed:
      0.03 +
      Math.random() *
        0.13,

    phase:
      Math.random() *
      Math.PI *
      2,

    alpha:
      0.12 +
      Math.random() *
        0.42,
  };
}

function drawFish(
  ctx: CanvasRenderingContext2D,
  fish: Fish,
  time: number,
) {

  const size =
    fish.size;

  const y =
    fish.y +
    Math.sin(
      time *
        0.0007 +
        fish.phase,
    ) *
      (5 +
        fish.depth *
          8);

  const glow =
    7 +
    fish.depth *
      14;

  ctx.save();

  ctx.translate(
    fish.x,
    y,
  );

  ctx.scale(
    fish.direction,
    1,
  );

  ctx.globalAlpha =
    0.35 +
    fish.depth *
      0.55;

  // ----------------------------------------------------------
  // Glow.
  // ----------------------------------------------------------

  ctx.shadowColor =
    fish.color;

  ctx.shadowBlur =
    glow;

  // ----------------------------------------------------------
  // Body.
  // ----------------------------------------------------------

  const body =
    ctx.createLinearGradient(
      -size,
      0,
      size,
      0,
    );

  body.addColorStop(
    0,
    fish.accent,
  );

  body.addColorStop(
    0.55,
    fish.color,
  );

  body.addColorStop(
    1,
    "rgba(255,255,255,0.15)",
  );

  ctx.fillStyle =
    body;

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
  // Tail.
  // ----------------------------------------------------------

  ctx.beginPath();

  ctx.moveTo(
    -size *
      0.62,
    0,
  );

  ctx.lineTo(
    -size *
      1.35,
    -size *
      0.55,
  );

  ctx.lineTo(
    -size *
      1.15,
    0,
  );

  ctx.lineTo(
    -size *
      1.35,
    size *
      0.55,
  );

  ctx.closePath();

  ctx.fillStyle =
    fish.accent;

  ctx.globalAlpha *=
    0.75;

  ctx.fill();

  // ----------------------------------------------------------
  // Fin.
  // ----------------------------------------------------------

  ctx.beginPath();

  ctx.moveTo(
    -size *
      0.05,
    -size *
      0.25,
  );

  ctx.lineTo(
    size *
      0.18,
    -size *
      0.78,
  );

  ctx.lineTo(
    size *
      0.38,
    -size *
      0.16,
  );

  ctx.closePath();

  ctx.fillStyle =
    fish.color;

  ctx.globalAlpha =
    0.55;

  ctx.fill();

  // ----------------------------------------------------------
  // Eye.
  // ----------------------------------------------------------

  ctx.shadowColor =
    "white";

  ctx.shadowBlur =
    5;

  ctx.fillStyle =
    "white";

  ctx.globalAlpha =
    0.92;

  ctx.beginPath();

  ctx.arc(
    size *
      0.42,
    -size *
      0.04,
    Math.max(
      0.8,
      size *
        0.085,
    ),
    0,
    Math.PI * 2,
  );

  ctx.fill();

  // ----------------------------------------------------------
  // Bioluminescent dots.
  // ----------------------------------------------------------

  ctx.shadowColor =
    fish.color;

  ctx.shadowBlur =
    9;

  ctx.fillStyle =
    fish.color;

  ctx.globalAlpha =
    0.9;

  ctx.beginPath();

  ctx.arc(
    -size *
      0.15,
    size *
      0.05,
    Math.max(
      0.6,
      size *
        0.05,
    ),
    0,
    Math.PI * 2,
  );

  ctx.fill();

  ctx.beginPath();

  ctx.arc(
    size *
      0.04,
    size *
      0.08,
    Math.max(
      0.55,
      size *
        0.045,
    ),
    0,
    Math.PI * 2,
  );

  ctx.fill();

  ctx.restore();
}

export default function OceanBackground() {

  const canvasRef =
    useRef<HTMLCanvasElement | null>(
      null,
    );

  useEffect(() => {

    const canvas =
      canvasRef.current;

    if (!canvas) {
      return;
    }

    const ctx =
      canvas.getContext(
        "2d",
      );

    if (!ctx) {
      return;
    }

    let width =
      window.innerWidth;

    let height =
      window.innerHeight;

    let dpr =
      Math.min(
        window.devicePixelRatio ||
          1,
        2,
      );

    let destroyed =
      false;

    let animationFrame =
      0;

    let fish: Fish[] =
      [];

    let particles:
      Particle[] =
      [];

    const resize = () => {

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

      fish =
        Array.from(
          {
            length:
              15,
          },
          () =>
            makeFish(
              width,
              height,
            ),
        );

      particles =
        Array.from(
          {
            length:
              140,
          },
          () =>
            makeParticle(
              width,
              height,
            ),
        );
    };

    // --------------------------------------------------------
    // Draw frame.
    // --------------------------------------------------------

    const render =
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

        // ====================================================
        // BLACK BACKGROUND
        // ====================================================

        ctx.fillStyle =
          "#000000";

        ctx.fillRect(
          0,
          0,
          width,
          height,
        );

        // ====================================================
        // VERY SUBTLE CENTER ATMOSPHERE
        // ====================================================

        const centerGlow =
          ctx.createRadialGradient(
            width *
              0.5,
            height *
              0.42,
            0,
            width *
              0.5,
            height *
              0.42,
            width *
              0.55,
          );

        centerGlow.addColorStop(
          0,
          "rgba(30,170,190,0.035)",
        );

        centerGlow.addColorStop(
          0.45,
          "rgba(15,90,110,0.018)",
        );

        centerGlow.addColorStop(
          1,
          "rgba(0,0,0,0)",
        );

        ctx.fillStyle =
          centerGlow;

        ctx.fillRect(
          0,
          0,
          width,
          height,
        );

        // ====================================================
        // PARTICLES
        // ====================================================

        ctx.shadowBlur =
          0;

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
            0.035;

          if (
            particle.y <
            -5
          ) {

            particle.y =
              height +
              5;

            particle.x =
              Math.random() *
              width;
          }

          const pulse =
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
              170,
              245,
              255,
              ${
                particle.alpha *
                pulse
              }
            )`;

          ctx.fill();
        }

        // ====================================================
        // CURRENT LINES
        // ====================================================

        ctx.save();

        ctx.globalAlpha =
          0.07;

        ctx.strokeStyle =
          "rgba(90,230,240,0.7)";

        ctx.lineWidth =
          1;

        for (
          let band = 0;
          band < 8;
          band++
        ) {

          const yBase =
            height *
            (
              0.09 +
              band *
                0.12
            );

          ctx.beginPath();

          for (
            let x = -30;
            x <
            width + 30;
            x += 26
          ) {

            const y =
              yBase +
              Math.sin(
                x *
                  0.009 +
                  time *
                    0.00018 +
                  band,
              ) *
                10;

            if (
              x ===
              -30
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

          ctx.stroke();
        }

        ctx.restore();

        // ====================================================
        // FISH
        // ====================================================

        for (
          const swimmer of
            fish
        ) {

          swimmer.x +=
            swimmer.speed *
            swimmer.direction *
            16;

          if (
            swimmer.direction >
            0 &&
            swimmer.x >
            width + 120
          ) {

            swimmer.x =
              -120;

            swimmer.y =
              Math.random() *
                height *
                0.86 +
              height *
                0.07;
          }

          if (
            swimmer.direction <
            0 &&
            swimmer.x <
            -120
          ) {

            swimmer.x =
              width + 120;

            swimmer.y =
              Math.random() *
                height *
                0.86 +
              height *
                0.07;
          }

          drawFish(
            ctx,
            swimmer,
            time,
          );
        }

        // ====================================================
        // VIGNETTE
        // ====================================================

        const vignette =
          ctx.createRadialGradient(
            width *
              0.5,
            height *
              0.5,
            height *
              0.15,
            width *
              0.5,
            height *
              0.5,
            Math.max(
              width,
              height,
            ) *
              0.78,
          );

        vignette.addColorStop(
          0,
          "rgba(0,0,0,0)",
        );

        vignette.addColorStop(
          0.78,
          "rgba(0,0,0,0.18)",
        );

        vignette.addColorStop(
          1,
          "rgba(0,0,0,0.72)",
        );

        ctx.fillStyle =
          vignette;

        ctx.fillRect(
          0,
          0,
          width,
          height,
        );

        if (
          document.visibilityState !==
          "hidden"
        ) {

          animationFrame =
            window.requestAnimationFrame(
              render,
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

    animationFrame =
      window.requestAnimationFrame(
        render,
      );

    return () => {

      destroyed =
        true;

      window.removeEventListener(
        "resize",
        resize,
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
        z-[1]
        overflow-hidden
      "
    >

      <canvas
        ref={canvasRef}
        className="
          absolute
          inset-0
          block
          h-full
          w-full
        "
      />

    </div>
  );
}
