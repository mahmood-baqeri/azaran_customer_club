//  src/shared/utils/currency.ts


export const persianToEnglish = (persianString: string): string => {
    const persianDigits: string[] = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    const englishDigits: string[] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    let englishString: string = persianString;

    for (let i = 0; i < persianDigits.length; i++) {
        // استفاده از RegExp برای جایگزینی تمام ارقام فارسی با معادل انگلیسی آن‌ها
        const regex = new RegExp(persianDigits[i], 'g');
        englishString = englishString.replace(regex, englishDigits[i]);
    }

    return englishString;
};