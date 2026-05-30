'use client';

import * as React from 'react';
import {
  motion,
  useMotionValue,
  useSpring,
  AnimatePresence,
  type HTMLMotionProps,
} from 'framer-motion';

type SpringOptions = {
  stiffness?: number;
  damping?: number;
  bounce?: number;
  mass?: number;
  velocity?: number;
  restSpeed?: number;
  restDelta?: number;
};

import { getStrictContext } from '@/lib/get-strict-context';
import { Slot, type WithAsChild } from '@/components/animate-ui/primitives/animate/slot';

type CursorContextType = {
  cursorPos: { x: number; y: number };
  active: boolean;
  global: boolean;
  containerRef: React.RefObject<HTMLDivElement | null>;
  cursorRef: React.RefObject<HTMLDivElement | null>;
};

const [LocalCursorProvider, useCursor] =
  getStrictContext<CursorContextType>('CursorContext');

type CursorProviderProps = {
  children: React.ReactNode;
  global?: boolean;
};

function CursorProvider({ children, global = false }: CursorProviderProps) {
  const [cursorPos, setCursorPos] = React.useState({ x: 0, y: 0 });
  const [active, setActive] = React.useState(false);

  const containerRef = React.useRef<HTMLDivElement>(null);
  const cursorRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const id = '__cursor_none_style__';
    if (document.getElementById(id)) return;

    const style = document.createElement('style');
    style.id = id;
    style.textContent = `
      .animate-ui-cursor-none, .animate-ui-cursor-none * { cursor: none !important; }
    `;
    document.head.appendChild(style);
  }, []);

  React.useEffect(() => {
    let removeListeners: () => void;

    if (global) {
      const handlePointerMove = (e: PointerEvent) => {
        setCursorPos({ x: e.clientX, y: e.clientY });
        setActive(true);
      };

      const handlePointerOut = (e: PointerEvent | MouseEvent) => {
        if (e instanceof PointerEvent && e.relatedTarget === null) {
          setActive(false);
        }
      };

      const handleVisibilityChange = () => {
        if (document.visibilityState === 'hidden') setActive(false);
      };

      window.addEventListener('pointermove', handlePointerMove, {
        passive: true,
      });
      window.addEventListener('pointerout', handlePointerOut, {
        passive: true,
      });
      window.addEventListener('mouseout', handlePointerOut, { passive: true });
      document.addEventListener('visibilitychange', handleVisibilityChange);

      removeListeners = () => {
        window.removeEventListener('pointermove', handlePointerMove);
        window.removeEventListener('pointerout', handlePointerOut);
        window.removeEventListener('mouseout', handlePointerOut);
        document.removeEventListener(
          'visibilitychange',
          handleVisibilityChange,
        );
      };
    } else {
      if (!containerRef.current) return;

      const parent = containerRef.current.parentElement;
      if (!parent) return;

      if (getComputedStyle(parent).position === 'static') {
        parent.style.position = 'relative';
      }

      const handlePointerMove = (e: PointerEvent) => {
        const rect = parent.getBoundingClientRect();
        setCursorPos({ x: e.clientX - rect.left, y: e.clientY - rect.top });
        setActive(true);
      };

      const handlePointerOut = (e: PointerEvent | MouseEvent) => {
        if (
          e.relatedTarget === null ||
          !(parent as Node).contains(e.relatedTarget as Node)
        ) {
          setActive(false);
        }
      };

      parent.addEventListener('pointermove', handlePointerMove, {
        passive: true,
      });
      parent.addEventListener('pointerout', handlePointerOut, {
        passive: true,
      });
      parent.addEventListener('mouseout', handlePointerOut, { passive: true });

      removeListeners = () => {
        parent.removeEventListener('pointermove', handlePointerMove);
        parent.removeEventListener('pointerout', handlePointerOut);
        parent.removeEventListener('mouseout', handlePointerOut);
      };
    }

    return removeListeners;
  }, [global]);

  return (
    <LocalCursorProvider
      value={{ cursorPos, active, global, containerRef, cursorRef }}
    >
      {children}
    </LocalCursorProvider>
  );
}

type CursorContainerProps = WithAsChild<HTMLMotionProps<'div'>>;

const CursorContainer = React.forwardRef<HTMLDivElement, CursorContainerProps>((
  { asChild = false, ...props },
  ref
) => {
  const { containerRef, global, active } = useCursor();
  React.useImperativeHandle(ref, () => containerRef.current as HTMLDivElement);

  if (asChild) {
    return (
      <Slot
        ref={containerRef as any}
        data-slot="cursor-container"
        data-global={global}
        data-active={active}
        {...props as any}
      />
    );
  }

  return (
    <motion.div
      ref={containerRef as any}
      data-slot="cursor-container"
      data-global={global}
      data-active={active}
      {...props as any}
    />
  );
});
CursorContainer.displayName = 'CursorContainer';

type CursorProps = WithAsChild<
  HTMLMotionProps<'div'> & {
    children: React.ReactNode;
  }
>;

const Cursor = React.forwardRef<HTMLDivElement, CursorProps>((
  { asChild = false, style, ...props },
  ref
) => {
  const { cursorPos, active, containerRef, cursorRef, global } = useCursor();
  React.useImperativeHandle(ref, () => cursorRef.current as HTMLDivElement);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  React.useEffect(() => {
    const target = global
      ? document.documentElement
      : containerRef.current?.parentElement;

    if (!target) return;

    if (active) {
      target.classList.add('animate-ui-cursor-none');
    } else {
      target.classList.remove('animate-ui-cursor-none');
    }

    return () => {
      target.classList.remove('animate-ui-cursor-none');
    };
  }, [active, global, containerRef]);

  React.useEffect(() => {
    x.set(cursorPos.x);
    y.set(cursorPos.y);
  }, [cursorPos, x, y]);

  const styleProps = {
    transform: 'translate(-50%,-50%)',
    pointerEvents: 'none' as any,
    zIndex: 9999,
    position: (global ? 'fixed' : 'absolute') as any,
    top: y,
    left: x,
    ...style,
  };

  return (
    <AnimatePresence>
      {active && (
        asChild ? (
          <Slot
            ref={cursorRef as any}
            data-slot="cursor"
            data-global={global}
            data-active={active}
            style={styleProps}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            {...props as any}
          />
        ) : (
          <motion.div
            ref={cursorRef as any}
            data-slot="cursor"
            data-global={global}
            data-active={active}
            style={styleProps}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            {...props as any}
          />
        )
      )}
    </AnimatePresence>
  );
});
Cursor.displayName = 'Cursor';

type CursorFollowSide = 'top' | 'right' | 'bottom' | 'left';
type CursorFollowAlign = 'start' | 'center' | 'end';

type CursorFollowProps = WithAsChild<
  Omit<HTMLMotionProps<'div'>, 'transition'> & {
    side?: CursorFollowSide;
    sideOffset?: number;
    align?: CursorFollowAlign;
    alignOffset?: number;
    transition?: SpringOptions;
    children: React.ReactNode;
  }
>;

const CursorFollow = React.forwardRef<HTMLDivElement, CursorFollowProps>((
  {
    asChild = false,
    side = 'bottom',
    sideOffset = 0,
    align = 'end',
    alignOffset = 0,
    style,
    transition = { stiffness: 500, damping: 50, bounce: 0 },
    ...props
  },
  ref
) => {
  const { cursorPos, active, cursorRef, global } = useCursor();
  const cursorFollowRef = React.useRef<HTMLDivElement>(null);
  React.useImperativeHandle(
    ref,
    () => cursorFollowRef.current as HTMLDivElement,
  );

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const springX = useSpring(x, transition);
  const springY = useSpring(y, transition);

  const calculateOffset = React.useCallback(() => {
    const rect = cursorFollowRef.current?.getBoundingClientRect();
    const width = rect?.width ?? 0;
    const height = rect?.height ?? 0;

    let offsetX = 0;
    let offsetY = 0;

    switch (side) {
      case 'top':
        offsetY = height + sideOffset;
        switch (align) {
          case 'start':
            offsetX = width + alignOffset;
            break;
          case 'center':
            offsetX = width / 2;
            break;
          case 'end':
            offsetX = -alignOffset;
            break;
        }
        break;

      case 'bottom':
        offsetY = -sideOffset;
        switch (align) {
          case 'start':
            offsetX = width + alignOffset;
            break;
          case 'center':
            offsetX = width / 2;
            break;
          case 'end':
            offsetX = -alignOffset;
            break;
        }
        break;

      case 'left':
        offsetX = width + sideOffset;
        switch (align) {
          case 'start':
            offsetY = height + alignOffset;
            break;
          case 'center':
            offsetY = height / 2;
            break;
          case 'end':
            offsetY = -alignOffset;
            break;
        }
        break;

      case 'right':
        offsetX = -sideOffset;
        switch (align) {
          case 'start':
            offsetY = height + alignOffset;
            break;
          case 'center':
            offsetY = height / 2;
            break;
          case 'end':
            offsetY = -alignOffset;
            break;
        }
        break;
    }

    return { x: offsetX, y: offsetY };
  }, [side, align, sideOffset, alignOffset]);

  React.useEffect(() => {
    const offset = calculateOffset();
    const cursorRect = cursorRef.current?.getBoundingClientRect();
    const cursorWidth = cursorRect?.width ?? 20;
    const cursorHeight = cursorRect?.height ?? 20;

    x.set(cursorPos.x - offset.x + cursorWidth / 2);
    y.set(cursorPos.y - offset.y + cursorHeight / 2);
  }, [calculateOffset, cursorPos, cursorRef, x, y]);

  const styleProps = {
    transform: 'translate(-50%,-50%)',
    pointerEvents: 'none' as any,
    zIndex: 9998,
    position: (global ? 'fixed' : 'absolute') as any,
    top: springY,
    left: springX,
    ...style,
  };

  return (
    <AnimatePresence>
      {active && (
        asChild ? (
          <Slot
            ref={cursorFollowRef}
            data-slot="cursor-follow"
            data-global={global}
            data-active={active}
            style={styleProps}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            {...props as any}
          />
        ) : (
          <motion.div
            ref={cursorFollowRef}
            data-slot="cursor-follow"
            data-global={global}
            data-active={active}
            style={styleProps}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            {...props as any}
          />
        )
      )}
    </AnimatePresence>
  );
});
CursorFollow.displayName = 'CursorFollow';

export {
  CursorProvider,
  Cursor,
  CursorContainer,
  CursorFollow,
  // eslint-disable-next-line react-refresh/only-export-components
  useCursor,
  type CursorProviderProps,
  type CursorProps,
  type CursorContainerProps,
  type CursorFollowProps,
  type CursorFollowAlign,
  type CursorFollowSide,
  type CursorContextType,
};
