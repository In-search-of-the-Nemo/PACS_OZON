export function loadComponents() {
  const result: Component[] = [];
  const modules = import.meta.glob("./components/*.ts", { eager: true });
  for (const path in modules) {
    const mod: any = modules[path];
    if (mod.default) {
      result.push(mod.default);
    }
  }

  result.sort((a, b) => (a.menuOrder ?? 0) - (b.menuOrder ?? 0));

  return result;
}

interface Component {
  name: string;
  // Lower values sort earlier; omitted defaults to 0, and equal values keep glob order.
  menuOrder?: number;
  factory: (container: { element: HTMLElement }) => void | (() => void);
  // returns unsubscribe function for every topic (bus.on)
}

export default Component;
