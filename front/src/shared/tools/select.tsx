// src/tools/select.tsx

import Select, {
  components,
  OptionProps,
  ValueContainerProps,
  GroupBase,
} from "react-select";

// -------------------------------------------------------------
// نوع پایه Option
// -------------------------------------------------------------
export interface Option {
  label: string;
  value: string | number;
}

// -------------------------------------------------------------
// Props مشترک
// -------------------------------------------------------------
type BaseProps = {
  options: Option[];
  placeholder?: string;
  isDisabled?: boolean;
  isLoading?: boolean;
  isClearable?: boolean;
  isSearchable?: boolean;
  className?: string;
  /** برای فرم‌ها */
  name?: string;
  /** پیام "هیچ گزینه‌ای انتخاب نشده" */
  noOptionsMessage?: string;
};

// -------------------------------------------------------------
// Props برای حالت Multi
// -------------------------------------------------------------
interface MultiProps extends BaseProps {
  isMulti: true;
  value: Option[];
  onChange: (selected: Option[]) => void;
}

// -------------------------------------------------------------
// Props برای حالت Single
// -------------------------------------------------------------
interface SingleProps extends BaseProps {
  isMulti?: false;
  value: Option | null;
  onChange: (selected: Option | null) => void;
}

export type SelectProps = MultiProps | SingleProps;

// -------------------------------------------------------------
// ✅ چک‌باکس در گزینه‌ها (فقط در multi معنا دارد)
// -------------------------------------------------------------
const CheckboxOption = (props: OptionProps<Option, boolean>) => {
  const { isSelected, label } = props;
  return (
    <components.Option {...props} className="option">
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input type="checkbox" checked={isSelected} readOnly />
        <label>{label}</label>
      </div>
    </components.Option>
  );
};

// -------------------------------------------------------------
// ✅ خلاصه‌سازی انتخاب‌ها (فقط در multi معنا دارد)
// -------------------------------------------------------------
const MultiValueContainer = (props: ValueContainerProps<Option, boolean>) => {
  const { getValue, hasValue } = props;
  const values = getValue();

  if (hasValue && values.length > 1) {
    return (
      <components.ValueContainer {...props}>
        {`${values.length} مورد انتخاب شده`}
      </components.ValueContainer>
    );
  }

  return <components.ValueContainer {...props} />;
};

// -------------------------------------------------------------
// ✅ کامپوننت اصلی
// -------------------------------------------------------------
const SelectElement = <IsMulti extends boolean = false>(
  props: IsMulti extends true ? MultiProps : SingleProps
) => {
  const {
    options,
    value,
    onChange,
    placeholder = "انتخاب کنید...",
    isDisabled,
    isLoading,
    isClearable,
    isSearchable = true,
    className,
    name,
    noOptionsMessage,
  } = props as SelectProps;

  const isMulti = (props as MultiProps).isMulti === true;

  const customComponents = isMulti
    ? {
      Option: CheckboxOption,
      ValueContainer: MultiValueContainer,
    }
    : undefined;

  return (
    <div className="selectElement">
      <Select<Option, boolean, GroupBase<Option>>
        isMulti={isMulti}
        options={options}
        value={value as Option | Option[] | null}
        onChange={(selected) => {
          if (isMulti) {
            (onChange as (s: Option[]) => void)((selected as Option[]) ?? []);
          } else {
            (onChange as (s: Option | null) => void)(selected as Option | null);
          }
        }}
        placeholder={placeholder}
        closeMenuOnSelect={!isMulti}
        hideSelectedOptions={false}
        components={customComponents}
        classNamePrefix="react-select"
        className={className}
        isDisabled={isDisabled}
        isLoading={isLoading}
        isClearable={isClearable ?? !isMulti}
        isSearchable={isSearchable}
        name={name}
        noOptionsMessage={noOptionsMessage ? () => noOptionsMessage : undefined}
      />
    </div>
  );
};

export default SelectElement;




/*


const [value, setValue] = useState<Option[]>([]);

<SelectElement
  isMulti
  options={OPTIONS}
  value={value}
  onChange={setValue}
/>



const [value, setValue] = useState<Option | null>(null);

<SelectElement
  options={OPTIONS}
  value={value}
  onChange={setValue}
/>



*/