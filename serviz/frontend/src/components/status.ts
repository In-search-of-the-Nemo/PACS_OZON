import Component from "../loadComponents";
import { bus, subscribeToTopic } from "../socketManager";

interface ObjectInfo {
  length_mm?: number | null;
  width_mm?: number | null;
  height_mm?: number | null;
  has_circle?: boolean | null;                    // наличие круга в сечении
}

interface State {
  status?: "ok" | "error" | string | null;        // работа / ошибка
  object?: ObjectInfo | null;                     // параметры текущего объекта
  categories?: Record<string, number> | null;     // счётчики по категориям
}

const STATUS_TOPIC = "status";

const DASH = "—";

const Status: Component = {
  name: "Status",
  menuOrder: -10, // главный компонент — первым в меню
  factory: (container) => {
    const root = container.element;
    root.style.display = "flex";
    root.style.flexDirection = "column";
    root.style.gap = "8px";
    root.style.height = "100%";
    root.style.padding = "8px";
    root.style.boxSizing = "border-box";
    root.style.overflowY = "auto";
    root.style.background = "#1d1d1d";
    root.style.color = "#b0b0b0";
    root.style.font = "14px Arial, sans-serif";

    // --- Секция: статус ---
    const statusSection = makeSection("Статус");
    const statusBadge = document.createElement("span");
    statusBadge.style.display = "inline-block";
    statusBadge.style.padding = "4px 12px";
    statusBadge.style.borderRadius = "4px";
    statusBadge.style.fontWeight = "bold";
    statusBadge.style.color = "#fff";
    statusSection.body.appendChild(statusBadge);

    // --- Секция: параметры текущего объекта ---
    const objectSection = makeSection("Текущий объект");
    const dims = {
      length: makeField("Длина", "мм"),
      width: makeField("Ширина", "мм"),
      height: makeField("Высота", "мм"),
      circle: makeField("Круг в сечении", ""),
    };
    const objectGrid = document.createElement("div");
    objectGrid.style.display = "grid";
    objectGrid.style.gridTemplateColumns = "auto 1fr";
    objectGrid.style.rowGap = "4px";
    objectGrid.style.columnGap = "12px";
    for (const f of Object.values(dims)) {
      objectGrid.append(f.labelEl, f.valueEl);
    }
    objectSection.body.appendChild(objectGrid);

    // --- Секция: счётчики по категориям ---
    const categoriesSection = makeSection("Категории");
    const categoriesBody = document.createElement("div");
    categoriesBody.style.display = "flex";
    categoriesBody.style.flexDirection = "column";
    categoriesBody.style.gap = "2px";
    categoriesSection.body.appendChild(categoriesBody);

    root.append(
      statusSection.root,
      objectSection.root,
      categoriesSection.root,
    );

    // --- Рендер состояния ---
    function render(state: State) {
      // Статус
      const status = state.status ?? null;
      const isOk = status === "ok" || status === "работа" || status === "run";
      const isError =
        status === "error" || status === "ошибка" || status === "fault";
      if (isOk) {
        statusBadge.textContent = "Работа";
        statusBadge.style.background = "#2e7d32";
      } else if (isError) {
        statusBadge.textContent = "Ошибка";
        statusBadge.style.background = "#c62828";
      } else {
        statusBadge.textContent = status ? String(status) : "нет данных";
        statusBadge.style.background = "#555";
      }

      // Параметры объекта
      const obj = state.object ?? null;
      dims.length.valueEl.textContent = fmtNum(obj?.length_mm);
      dims.width.valueEl.textContent = fmtNum(obj?.width_mm);
      dims.height.valueEl.textContent = fmtNum(obj?.height_mm);
      dims.circle.valueEl.textContent =
        obj?.has_circle == null ? DASH : obj.has_circle ? "да" : "нет";

      // Категории
      categoriesBody.replaceChildren();
      const categories = state.categories ?? {};
      const keys = Object.keys(categories);
      if (keys.length === 0) {
        const empty = document.createElement("div");
        empty.textContent = DASH;
        empty.style.color = "#666";
        categoriesBody.appendChild(empty);
      } else {
        for (const key of keys) {
          const row = document.createElement("div");
          row.style.display = "flex";
          row.style.justifyContent = "space-between";
          row.style.borderBottom = "1px solid #333";
          row.style.padding = "2px 0";
          const name = document.createElement("span");
          name.textContent = key;
          const count = document.createElement("span");
          count.textContent = String(categories[key]);
          count.style.fontWeight = "bold";
          count.style.color = "#ddd";
          row.append(name, count);
          categoriesBody.appendChild(row);
        }
      }
    }

    render({});

    const onState = (payload: State) => render(payload ?? {});
    subscribeToTopic(STATUS_TOPIC);
    bus.on(STATUS_TOPIC, onState);

    return () => {
      bus.off(STATUS_TOPIC, onState);
    };
  },
};

export default Status;

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function makeSection(title: string): {
  root: HTMLElement;
  body: HTMLElement;
} {
  const root = document.createElement("div");
  root.style.background = "#242424";
  root.style.borderRadius = "6px";
  root.style.overflow = "hidden";

  const header = document.createElement("div");
  header.textContent = title;
  header.style.padding = "6px 10px";
  header.style.background = "#1a1a1a";
  header.style.fontWeight = "bold";
  header.style.color = "#ddd";
  header.style.userSelect = "none";

  const body = document.createElement("div");
  body.style.padding = "10px";

  root.append(header, body);
  return { root, body };
}

function makeField(label: string, unit: string): {
  labelEl: HTMLElement;
  valueEl: HTMLElement;
} {
  const labelEl = document.createElement("span");
  labelEl.textContent = unit ? `${label}, ${unit}` : label;
  labelEl.style.color = "#8a8a8a";

  const valueEl = document.createElement("span");
  valueEl.textContent = DASH;
  valueEl.style.color = "#ddd";
  valueEl.style.textAlign = "right";

  return { labelEl, valueEl };
}

function fmtNum(value: number | null | undefined): string {
  return value == null ? DASH : String(Math.round(value));
}
