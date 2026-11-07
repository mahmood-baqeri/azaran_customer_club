import React, { useEffect, useState } from 'react';
import { Domain_Manager } from '../constants/env';




//##################################################################################
//##################################################################################
//##################################################################################
//##################################################################################
//############################             
//############################                  Input Box
interface InputBoxProps {
  label?: string;
  value: string | number;
  required?: boolean;
  disabled?: boolean;
  onChange: (value: string | number) => void;
  type?: 'text' | 'number' | 'email' | 'time' | 'password' | 'textarea';
  placeholder?: string;
  name?: string;
  rows?: number; // فقط برای textarea
}

export const InputBox: React.FC<InputBoxProps> = ({
  label,
  value,
  required = false,
  disabled = false,
  onChange,
  type = 'text',
  placeholder,
  name,
  rows = 4,
}) => {
  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const val = type === 'number' ? Number(e.target.value) : e.target.value;
    onChange(val);
  };

  return (
    <div className="mb-2">
      {label && (
        <label className="form-label" htmlFor={name}>
          {required && <span className="text-danger ms-2"> *</span>}
          {label}
        </label>
      )}

      {type === 'textarea' ? (
        <textarea
          id={name}
          name={name}
          className="form-control textarea"
          value={value}
          required={required}
          disabled={disabled}
          placeholder={placeholder}
          rows={rows}
          onChange={handleChange}
        />
      ) : (
        <input
          id={name}
          name={name}
          type={type}
          className="form-control textbox"
          value={value}
          required={required}
          disabled={disabled}
          placeholder={placeholder}
          onChange={handleChange}
        />
      )}
    </div>
  );
};
/*

const [bio, setBio] = useState('');
const [email, setEmail] = useState('');
<form>
    <InputBox
    label="ایمیل"
    name="email"
    type="email"
    value={email}
    onChange={(val) => setEmail(val as string)}
    required
    />

    <InputBox
    label="بیوگرافی"
    name="bio"
    type="textarea"
    value={bio}
    onChange={(val) => setBio(val as string)}
    placeholder="درباره‌ی خودتان بنویسید"
    rows={5}
    />

*/



//##################################################################################
//##################################################################################
//##################################################################################
//##################################################################################
//############################             
//############################                  Check Box
interface CheckBoxProps {
  label?: string;
  checked: boolean;
  required?: boolean;
  onChange: (checked: boolean) => void;
  name?: string;
  disabled?: boolean;
}

export const CheckBox: React.FC<CheckBoxProps> = ({
  label,
  checked,
  required = false,
  onChange,
  name,
  disabled = false,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.checked);
  };

  return (
    <label className="form-check mb-3 checkBoxElement form-check-label pe-4 position-relative">
      <input
        className="form-check-input"
        type="checkbox"
        id={name}
        name={name}
        checked={checked}
        required={required}
        onChange={handleChange}
        disabled={disabled}
      />
      {label && (
        <span >
          {required && <span className="text-danger ms-2" style={{ position: "absolute", marginRight: "-12px" }}> *</span>}
          <b className='me-4 fs-12'>{label}</b>
        </span>
      )}
    </label >
  );
};



//##################################################################################
//##################################################################################
//##################################################################################
//##################################################################################
//############################             
//############################                  Radio Box
interface RadioOption {
  label: string;
  value: string;
  disabled?: boolean;
}

interface RadioGroupProps {
  label?: string;
  name: string;
  options: RadioOption[];
  selectedValue: string;
  onChange: (value: string) => void;
  required?: boolean;
}

export const RadioGroup: React.FC<RadioGroupProps> = ({
  label,
  name,
  options,
  selectedValue,
  onChange,
  required = false,
}) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className="mb-2">
      {label && (
        <div className="form-label">
          {required && <span className="text-danger ms-2"> *</span>}
          {label}
        </div>
      )}

      {options.map((option, index) => (
        <div className="form-check radioBoxElement" key={index}>
          <input
            className="form-check-input"
            type="radio"
            name={name}
            id={`${name}-${index}`}
            value={option.value}
            checked={selectedValue === option.value}
            onChange={handleChange}
            required={required && index === 0} // فقط برای اولین گزینه الزامی باشه
            disabled={option.disabled}
          />
          <label className="form-check-label" htmlFor={`${name}-${index}`}>
            {option.label}
          </label>
        </div>
      ))}
    </div>
  );
};

/*
const [gender, setGender] = useState('female');
const genderOptions = [
  { label: 'زن', value: 'female' },
  { label: 'مرد', value: 'male' },
  { label: 'سایر', value: 'other' },
];
<RadioGroup
    label="جنسیت"
    name="gender"
    options={genderOptions}
    selectedValue={gender}
    onChange={setGender}
    required
/>
*/


//##################################################################################
//##################################################################################
//##################################################################################
//##################################################################################
//############################             
//############################                  Image Box

interface imgProps {
  img: string | File;
  onChange: (answer: string | File) => void;
}

export const ImageBox = ({ onChange, img }: imgProps) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      onChange(file);
    }
  };

  useEffect(() => {
    let url: string | null = null;

    if (img instanceof File) {
      url = URL.createObjectURL(img);
      setPreviewUrl(url);
    } else if (typeof img === 'string' && img != '') {
      setPreviewUrl(Domain_Manager + img);
    }

    return () => {
      if (url) {
        URL.revokeObjectURL(url);
      }
    };
  }, [img]);

  return (
    <div className="image-answer imageInputElement">
      <input type="file" accept="image/*" onChange={handleFileChange} className="form-control" />
      {previewUrl && (
        <div>
          <img
            src={previewUrl}
            alt="preview"
            style={{ maxWidth: '100%', height: 'auto', borderRadius: '8px' }}
          />
        </div>
      )}
    </div>
  );
};
