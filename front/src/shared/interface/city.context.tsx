import { ProvinceInterface } from "./province.context";

export interface CityInterface {
     id?: string;
     name?: string;
     province?: ProvinceInterface;
}