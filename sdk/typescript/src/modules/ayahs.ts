import * as AyahsType from "../types/ayahs";
import * as WordsType from "../types/words";
import { AxiosResponse } from "axios";
import { Connection } from "../client/connection";
import { BaseController } from "../utils/baseController";
import { RequestConfig } from "../utils/globalTypes";

export class AyahsController extends BaseController {

    constructor(connection: Connection, token?: string) {
        super(connection, token);
    }
    
    /** GET /ayahs/ */
    async list(config?: RequestConfig<AyahsType.AyahsListRequestParams>
    ): Promise<AxiosResponse<AyahsType.AyahsListResponseData>> {
        return await this.axiosGet(`/ayahs/`, config);
    }
    
    /** POST /ayahs/ */
    async create(data: AyahsType.AyahsCreateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<AyahsType.AyahsCreateResponseData>> {
        return await this.axiosPost(`/ayahs/`, data, config);
    }
    
    /** GET /ayahs/{uuid}/ */
    async retrieve(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<AyahsType.AyahsRetrieveResponseData>> {
        return await this.axiosGet(`/ayahs/${uuid}/`, config);
    }
    
    /** PUT /ayahs/{uuid}/ */
    async update(uuid: string, data: AyahsType.AyahsUpdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<AyahsType.AyahsUpdateResponseData>> {
        return await this.axiosPut(`/ayahs/${uuid}/`, data, config);
    }
    
    /** PATCH /ayahs/{uuid}/ */
    async partialUpdate(uuid: string, data: AyahsType.AyahsPartialupdateRequestData, config?: RequestConfig
    ): Promise<AxiosResponse<AyahsType.AyahsPartialupdateResponseData>> {
        return await this.axiosPatch(`/ayahs/${uuid}/`, data, config);
    }
    
    /** DELETE /ayahs/{uuid}/ */
    async delete(uuid: string, config?: RequestConfig
    ): Promise<AxiosResponse<any>> {
        return await this.axiosDelete(`/ayahs/${uuid}/`, config);
    }
    
}