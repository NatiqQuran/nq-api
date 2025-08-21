import * as SurahsType from "../types/surahs";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class SurahsController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /surahs/ */
    async list(config?: RequestConfig<SurahsType.SurahsListRequestParams>
    ): Promise<AxiosResponse<SurahsType.SurahsListResponseData>> {
        return await this.axiosGet(`/surahs/`, config);
    }
    
    /** POST /surahs/ */
    async create(data: SurahsType.SurahsCreateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<SurahsType.SurahsCreateResponseData>> {
        return await this.axiosPost(`/surahs/`, data, config);
    }
    
    /** GET /surahs/{uuid}/ */
    async retrieve(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<SurahsType.SurahsRetrieveResponseData>> {
        return await this.axiosGet(`/surahs/${uuid}/`, config);
    }
    
    /** PUT /surahs/{uuid}/ */
    async update(uuid: string,data: SurahsType.SurahsUpdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<SurahsType.SurahsUpdateResponseData>> {
        return await this.axiosPut(`/surahs/${uuid}/`, data, config);
    }
    
    /** PATCH /surahs/{uuid}/ */
    async partialUpdate(uuid: string,data: SurahsType.SurahsPartialupdateRequestData,config?: RequestConfig
    ): Promise<AxiosResponse<SurahsType.SurahsPartialupdateResponseData>> {
        return await this.axiosPatch(`/surahs/${uuid}/`, data, config);
    }
    
    /** DELETE /surahs/{uuid}/ */
    async delete(uuid: string,config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/surahs/${uuid}/`, config);
    }
    
}